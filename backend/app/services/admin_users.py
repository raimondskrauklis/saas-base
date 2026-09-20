# backend/app/services/admin_users.py
"""Platform admin user directory — P2."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import PlatformRole, UserStatus
from app.core.exceptions import NotFoundError, ValidationError
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


async def list_admin_users(
    session: AsyncSession,
    *,
    params: CursorParams,
    status: UserStatus | None = None,
    search: str | None = None,
) -> CursorResponse[AdminUserListItem]:
    stmt = select(UserORM)

    # Default: omit deleted
    if status is not None:
        stmt = stmt.where(UserORM.status == status)
    else:
        stmt = stmt.where(UserORM.status != UserStatus.deleted)

    trimmed_search = (search or "").strip()
    if trimmed_search:
        pattern = f"%{trimmed_search}%"
        stmt = stmt.where(
            or_(
                UserORM.email.ilike(pattern),
                UserORM.full_name.ilike(pattern),
            )
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
        rows = rows[: params.limit]

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
    session: AsyncSession,
    *,
    user_id: UUID,
) -> AdminUserDetail:
    user = await session.get(UserORM, user_id)
    if user is None:
        raise NotFoundError("User not found")

    # Memberships — join workspaces
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

    # Impersonate allowed: not SA and status == active
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