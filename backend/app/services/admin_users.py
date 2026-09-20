# backend/app/services/admin_users.py
"""Platform admin user directory + lifecycle mutations - P2/P3."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PlatformRole, UserStatus
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.pagination import (
    CursorMeta,
    CursorParams,
    CursorResponse,
    InvalidCursorError,
    decode_cursor,
    encode_cursor,
)
from app.models.users import UserORM
from app.models.workspace_memberships import WorkspaceMembershipORM
from app.models.workspaces import WorkspaceORM
from app.schemas.admin import (
    AdminUserDetail,
    AdminUserListItem,
    AdminWorkspaceMembershipOut,
)
from app.services.audit_service import record_audit
from app.services.integrations.keycloak_admin import KeycloakAdminClient, KeycloakAdminError
from app.services.onboarding import activate_user_with_workspace

# --- helpers ---


def _make_admin_client() -> KeycloakAdminClient:
    return KeycloakAdminClient()


async def _get_user_for_update(session: AsyncSession, user_id: UUID) -> UserORM:
    user = await session.scalar(
        select(UserORM).where(UserORM.id == user_id).with_for_update()
    )
    if user is None:
        raise NotFoundError("User not found")
    return user


async def _count_active_super_admins(session: AsyncSession) -> int:
    count = await session.scalar(
        select(func.count())
        .select_from(UserORM)
        .where(
            UserORM.platform_role == PlatformRole.super_admin,
            UserORM.status == UserStatus.active,
        )
    )
    return int(count or 0)


# --- Q22 dual-write wrapper ---


@asynccontextmanager
async def dual_write_user_enabled(
    session: AsyncSession,
    *,
    user: UserORM,
    target_enabled: bool,
    logout: bool = False,
) -> AsyncIterator[UserORM]:
    """Mutate user, call Keycloak Admin, then commit. Restore KC on commit failure."""
    kc = _make_admin_client()
    try:
        yield user
        await session.flush()
        await kc.set_user_enabled(user.keycloak_user_id, enabled=target_enabled)
        if logout:
            await kc.logout_user(user.keycloak_user_id)
        try:
            await session.commit()
        except Exception:
            await kc.set_user_enabled(user.keycloak_user_id, enabled=not target_enabled)
            raise
    except KeycloakAdminError:
        raise
    finally:
        await kc.close()


# --- list + detail (P2) ---


async def list_admin_users(
    session: AsyncSession,
    *,
    params: CursorParams,
    status: UserStatus | None = None,
    search: str | None = None,
) -> CursorResponse[AdminUserListItem]:
    stmt = select(UserORM)
    if status is not None:
        stmt = stmt.where(UserORM.status == status)
    else:
        stmt = stmt.where(UserORM.status != UserStatus.deleted)

    trimmed_search = (search or "").strip()
    if trimmed_search:
        pattern = f"%{trimmed_search}%"
        stmt = stmt.where(
            or_(UserORM.email.ilike(pattern), UserORM.full_name.ilike(pattern))
        )

    if params.cursor:
        try:
            cursor_ts, cursor_id = decode_cursor(params.cursor)
        except InvalidCursorError as exc:
            raise ValidationError(message="Invalid cursor", field="cursor") from exc
        stmt = stmt.where(
            (UserORM.created_at < cursor_ts)
            | ((UserORM.created_at == cursor_ts) & (UserORM.id < cursor_id))
        )

    stmt = stmt.order_by(UserORM.created_at.desc(), UserORM.id.desc()).limit(
        params.limit + 1
    )
    result = await session.execute(stmt)
    rows = list(result.all())

    has_next = len(rows) > params.limit
    if has_next:
        rows = rows[:params.limit]

    items: list[AdminUserListItem] = []
    for (user,) in rows:
        items.append(
            AdminUserListItem(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                status=user.status,
                platform_role=user.platform_role,
                created_at=user.created_at,
            )
        )

    next_cursor = None
    if has_next and rows:
        (last_user,) = rows[-1]
        next_cursor = encode_cursor(last_user.created_at, last_user.id)

    return CursorResponse(
        items=items,
        cursor=CursorMeta(next_cursor=next_cursor, has_next=has_next),
    )


async def get_admin_user_detail(
    session: AsyncSession, *, user_id: UUID
) -> AdminUserDetail:
    user = await session.get(UserORM, user_id)
    if user is None:
        raise NotFoundError("User not found")

    memberships_result = await session.execute(
        select(WorkspaceMembershipORM, WorkspaceORM.name)
        .join(WorkspaceORM, WorkspaceORM.id == WorkspaceMembershipORM.workspace_id)
        .where(WorkspaceMembershipORM.user_id == user_id)
    )
    memberships = [
        AdminWorkspaceMembershipOut(
            workspace_id=wm.workspace_id,
            workspace_name=ws_name,
            role=wm.role,
        )
        for wm, ws_name in memberships_result.all()
    ]

    impersonate_allowed = (
        user.platform_role != PlatformRole.super_admin
        and user.status == UserStatus.active
    )

    return AdminUserDetail(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        status=user.status,
        platform_role=user.platform_role,
        impersonate_allowed=impersonate_allowed,
        memberships=memberships,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# --- suspend / reactivate (P3.2) ---


async def suspend_user(
    session: AsyncSession, *, user_id: UUID, actor_user_id: UUID
) -> UserORM:
    if actor_user_id == user_id:
        raise ForbiddenError(message="Cannot suspend your own account")

    user = await _get_user_for_update(session, user_id)
    if user.status != UserStatus.active:
        raise ValidationError(message="Only active users can be suspended")

    if user.platform_role == PlatformRole.super_admin:
        active_sas = await _count_active_super_admins(session)
        if active_sas <= 1:
            raise ForbiddenError(
                message="Cannot suspend the last active super admin",
                error_code="last_super_admin",
            )

    async with dual_write_user_enabled(
        session, user=user, target_enabled=False, logout=True
    ):
        user.status = UserStatus.suspended
        await session.flush()
        await record_audit(
            session,
            actor_user_id=actor_user_id,
            workspace_id=None,
            action="platform.user.suspended",
            resource_type="user",
            resource_id=str(user.id),
        )

    return user


async def reactivate_user(
    session: AsyncSession, *, user_id: UUID, actor_user_id: UUID
) -> UserORM:
    user = await _get_user_for_update(session, user_id)
    if user.status != UserStatus.suspended:
        raise ValidationError(message="Only suspended users can be reactivated")

    async with dual_write_user_enabled(
        session, user=user, target_enabled=True, logout=False
    ):
        user.status = UserStatus.active
        await session.flush()
        await record_audit(
            session,
            actor_user_id=actor_user_id,
            workspace_id=None,
            action="platform.user.reactivated",
            resource_type="user",
            resource_id=str(user.id),
        )

    return user


# --- approve / reject (P3.3) ---


async def approve_user(
    session: AsyncSession, *, user_id: UUID, actor_user_id: UUID
) -> UserORM:
    user = await _get_user_for_update(session, user_id)
    if user.status != UserStatus.pending_approval:
        raise ValidationError("User is not pending approval")

    kc = _make_admin_client()
    try:
        kc_user = await kc.get_user(user.keycloak_user_id)
    finally:
        await kc.close()

    email_verified = kc_user.get("emailVerified", False)
    needs_verify = not email_verified

    async with dual_write_user_enabled(
        session, user=user, target_enabled=True, logout=False
    ):
        if needs_verify:
            kc2 = _make_admin_client()
            try:
                await kc2.execute_actions_email(
                    user.keycloak_user_id, ["VERIFY_EMAIL"]
                )
            except KeycloakAdminError:
                raise
            finally:
                await kc2.close()

        display_name = (user.full_name or user.email).strip()
        await activate_user_with_workspace(session, user, name=display_name)
        await session.flush()
        await record_audit(
            session,
            actor_user_id=actor_user_id,
            workspace_id=None,
            action="platform.user.approved",
            resource_type="user",
            resource_id=str(user.id),
        )

    return user


async def reject_user(
    session: AsyncSession, *, user_id: UUID, actor_user_id: UUID
) -> UserORM:
    user = await _get_user_for_update(session, user_id)
    if user.status != UserStatus.pending_approval:
        raise ValidationError("User is not pending approval")

    async with dual_write_user_enabled(
        session, user=user, target_enabled=False, logout=True
    ):
        user.status = UserStatus.rejected
        await session.flush()
        await record_audit(
            session,
            actor_user_id=actor_user_id,
            workspace_id=None,
            action="platform.user.rejected",
            resource_type="user",
            resource_id=str(user.id),
        )

    return user


# --- send password reset (P3.4) ---


async def send_password_reset(session: AsyncSession, *, user_id: UUID) -> None:
    user = await session.get(UserORM, user_id)
    if user is None:
        raise NotFoundError("User not found")

    kc = _make_admin_client()
    try:
        await kc.execute_actions_email(user.keycloak_user_id, ["UPDATE_PASSWORD"])
    finally:
        await kc.close()
