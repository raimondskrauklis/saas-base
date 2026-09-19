# backend/app/services/keycloak_provisioning.py
"""Keycloak identity → PostgreSQL user provisioning — USER_PROVISIONING program.

JIT auth and KC webhooks call ``provision_user_from_keycloak`` (idempotent).
Invitees must be provisioned (JIT or webhook) before ``accept_invitation``.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import AppRole, PlatformRole, UserStatus, WorkspaceStatus
from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import get_logger
from app.core.sqlalchemy_errors import is_unique_violation
from app.models.users import UserORM
from app.models.workspace_memberships import WorkspaceMembershipORM
from app.models.workspaces import WorkspaceORM
from app.services.memberships import _count_workspace_admins
from app.services.onboarding import (
    maybe_auto_provision_user,
    resolve_initial_user_status,
)
from app.services.users import (
    activate_bootstrap_super_admin,
    get_user_by_email,
    get_user_by_keycloak_id,
)

logger = get_logger(__name__)


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def _assert_email_available(
    session: AsyncSession,
    email: str,
    *,
    excluding_user_id: UUID | None,
) -> None:
    existing = await get_user_by_email(session, email)
    if existing is None:
        return
    if excluding_user_id is not None and existing.id == excluding_user_id:
        return
    raise ConflictError(
        message="Email is already associated with another account",
        error_code="identity_email_conflict",
    )


async def _sync_user_email(
    session: AsyncSession,
    user: UserORM,
    email: str,
    *,
    email_verified: bool,
) -> None:
    if user.email == email:
        if email_verified and user.status == UserStatus.pending_email_verification:
            user.status = resolve_initial_user_status(email_verified=True)
            await session.flush()
        return

    await _assert_email_available(session, email, excluding_user_id=user.id)
    user.email = email
    if email_verified and user.status == UserStatus.pending_email_verification:
        user.status = resolve_initial_user_status(email_verified=True)
    await session.flush()


async def _find_bootstrap_seed(session: AsyncSession, email: str) -> UserORM | None:
    bootstrap_email = (settings.bootstrap_super_admin_email or "").strip().lower()
    if not bootstrap_email or email != bootstrap_email:
        return None
    seeded = await get_user_by_email(session, bootstrap_email)
    if seeded is None:
        return None
    if seeded.platform_role != PlatformRole.super_admin:
        return None
    if seeded.status not in (UserStatus.pending_activation, UserStatus.active):
        return None
    return seeded


async def _apply_live_identity(
    session: AsyncSession,
    user: UserORM,
    *,
    sub: str,
    email: str | None,
    email_verified: bool,
    display_name: str | None,
) -> UserORM:
    if user.status == UserStatus.deleted:
        return user
    if email and email.strip():
        await _sync_user_email(
            session,
            user,
            normalize_email(email),
            email_verified=email_verified,
        )
    if display_name:
        name = display_name.strip()
        if name and user.full_name != name:
            user.full_name = name
            await session.flush()
    user = await maybe_auto_provision_user(
        session,
        user,
        display_name=display_name,
        email_verified=email_verified,
    )
    return await activate_bootstrap_super_admin(session, user, sub=sub)


async def provision_user_from_keycloak(
    session: AsyncSession,
    *,
    sub: str,
    email: str | None,
    email_verified: bool,
    display_name: str | None = None,
) -> UserORM:
    """Create or update app user from Keycloak identity claims."""
    user = await get_user_by_keycloak_id(session, sub)
    has_email = bool(email and email.strip())

    if user is not None:
        return await _apply_live_identity(
            session,
            user,
            sub=sub,
            email=email,
            email_verified=email_verified,
            display_name=display_name,
        )

    if not has_email:
        raise UnauthorizedError(
            "User not provisioned",
            error_code="provision_email_required",
        )

    normalized = normalize_email(email)
    seeded = await _find_bootstrap_seed(session, normalized)
    if seeded is not None:
        return await activate_bootstrap_super_admin(session, seeded, sub=sub)

    await _assert_email_available(session, normalized, excluding_user_id=None)

    user = UserORM(
        keycloak_user_id=sub,
        email=normalized,
        status=resolve_initial_user_status(email_verified=email_verified),
    )
    session.add(user)
    try:
        async with session.begin_nested():
            await session.flush()
    except IntegrityError as exc:
        if not is_unique_violation(exc):
            raise
        session.expunge(user)
        existing = await get_user_by_keycloak_id(session, sub)
        if existing is None:
            existing = await get_user_by_email(session, normalized)
            if existing is None or existing.keycloak_user_id != sub:
                raise ConflictError(
                    message="Email is already associated with another account",
                    error_code="identity_email_conflict",
                ) from exc
        return await _apply_live_identity(
            session,
            existing,
            sub=sub,
            email=email,
            email_verified=email_verified,
            display_name=display_name,
        )
    logger.info(
        "user_provisioned",
        extra={"user_id": str(user.id), "operation": "provision_user_from_keycloak"},
    )

    user = await maybe_auto_provision_user(
        session,
        user,
        display_name=display_name,
        email_verified=email_verified,
    )
    return await activate_bootstrap_super_admin(session, user, sub=sub)


async def apply_keycloak_user_disabled(
    session: AsyncSession,
    *,
    sub: str,
    enabled: bool,
) -> UserORM | None:
    user = await get_user_by_keycloak_id(session, sub)
    if user is None:
        return None
    if enabled:
        if user.status == UserStatus.suspended:
            user.status = UserStatus.active
    else:
        user.status = UserStatus.suspended
    await session.flush()
    return user


async def _release_workspace_on_identity_deleted(
    session: AsyncSession,
    membership: WorkspaceMembershipORM,
) -> None:
    """KC DELETE cannot be blocked — transfer last admin or mark empty workspace deleted."""
    workspace_id = membership.workspace_id
    others = (
        await session.scalars(
            select(WorkspaceMembershipORM).where(
                WorkspaceMembershipORM.workspace_id == workspace_id,
                WorkspaceMembershipORM.user_id != membership.user_id,
            )
        )
    ).all()
    if not others:
        workspace = await session.get(WorkspaceORM, workspace_id)
        if workspace is not None and workspace.status != WorkspaceStatus.deleted:
            workspace.status = WorkspaceStatus.deleted
        await session.delete(membership)
        return
    if membership.role == AppRole.admin:
        admin_count = await _count_workspace_admins(session, workspace_id=workspace_id)
        if admin_count <= 1:
            others[0].role = AppRole.admin
    await session.delete(membership)


async def apply_keycloak_user_deleted(session: AsyncSession, *, sub: str) -> UserORM | None:
    user = await get_user_by_keycloak_id(session, sub)
    if user is None:
        return None
    memberships = (
        await session.scalars(
            select(WorkspaceMembershipORM).where(WorkspaceMembershipORM.user_id == user.id)
        )
    ).all()
    for membership in memberships:
        await _release_workspace_on_identity_deleted(session, membership)
    user.status = UserStatus.deleted
    user.email = f"deleted+{user.id}@app.invalid"
    user.full_name = None
    await session.flush()
    return user
