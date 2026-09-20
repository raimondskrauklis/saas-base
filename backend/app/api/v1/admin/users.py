# backend/app/api/v1/admin/users.py
"""Platform signup queue + user directory + lifecycle mutations - P2/P3."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.constants.enums import UserStatus
from app.core.auth import CurrentUser, require_impersonation_allowed, require_super_admin
from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.idempotency import idempotency_guard
from app.core.pagination import CursorParams, CursorResponse, get_cursor_params
from app.schemas.admin import AdminUserDetail, AdminUserListItem
from app.schemas.common import SuccessResponse
from app.schemas.me import MeResponse
from app.schemas.users import PendingUserResponse
from app.services.admin_users import (
    approve_user,
    reactivate_user,
    reject_user,
    send_password_reset,
    suspend_user,
)
from app.services.admin_users import get_admin_user_detail as _get_admin_user_detail
from app.services.admin_users import list_admin_users as _list_admin_users
from app.services.users import build_me_response, list_pending_users

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("/pending", response_model=SuccessResponse[list[PendingUserResponse]])
async def get_pending_users(
    _admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[list[PendingUserResponse]]:
    users = await list_pending_users(session)
    return SuccessResponse(
        data=[PendingUserResponse.model_validate(user) for user in users],
    )


@router.get("", response_model=SuccessResponse[CursorResponse[AdminUserListItem]])
async def get_admin_users(
    _admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
    params: Annotated[CursorParams, Depends(get_cursor_params)],
    status: Annotated[UserStatus | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=255)] = None,
) -> SuccessResponse[CursorResponse[AdminUserListItem]]:
    page = await _list_admin_users(
        session, params=params, status=status, search=search,
    )
    return SuccessResponse(data=page)


@router.get("/{user_id}", response_model=SuccessResponse[AdminUserDetail])
async def get_admin_user_detail(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[AdminUserDetail]:
    if admin.actor_user_id is None:
        raise UnauthorizedError("User not provisioned")
    detail = await _get_admin_user_detail(session, user_id=user_id)
    return SuccessResponse(data=detail)


@router.post("/{user_id}/approve", response_model=SuccessResponse[MeResponse])
async def post_approve_user(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
    idempotent: Annotated[JSONResponse | None, Depends(idempotency_guard)] = None,
) -> SuccessResponse[MeResponse] | JSONResponse:
    if idempotent is not None:
        return idempotent
    if admin.actor_user_id is None:
        raise UnauthorizedError("User not provisioned")
    user = await approve_user(session, user_id=user_id, actor_user_id=admin.actor_user_id)
    me = await build_me_response(session, user.id)
    return SuccessResponse(data=me)


@router.post("/{user_id}/reject", response_model=SuccessResponse[PendingUserResponse])
async def post_reject_user(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
    idempotent: Annotated[JSONResponse | None, Depends(idempotency_guard)] = None,
) -> SuccessResponse[PendingUserResponse] | JSONResponse:
    if idempotent is not None:
        return idempotent
    if admin.actor_user_id is None:
        raise UnauthorizedError("User not provisioned")
    user = await reject_user(session, user_id=user_id, actor_user_id=admin.actor_user_id)
    return SuccessResponse(data=PendingUserResponse.model_validate(user))


@router.post("/{user_id}/suspend", response_model=SuccessResponse[AdminUserDetail])
async def post_suspend_user(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[AdminUserDetail]:
    if admin.actor_user_id is None:
        raise UnauthorizedError("User not provisioned")
    await suspend_user(session, user_id=user_id, actor_user_id=admin.actor_user_id)
    detail = await _get_admin_user_detail(session, user_id=user_id)
    return SuccessResponse(data=detail)


@router.post("/{user_id}/reactivate", response_model=SuccessResponse[AdminUserDetail])
async def post_reactivate_user(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[AdminUserDetail]:
    if admin.actor_user_id is None:
        raise UnauthorizedError("User not provisioned")
    await reactivate_user(session, user_id=user_id, actor_user_id=admin.actor_user_id)
    detail = await _get_admin_user_detail(session, user_id=user_id)
    return SuccessResponse(data=detail)


@router.post(
    "/{user_id}/send-password-reset",
    response_model=SuccessResponse,
)
async def post_send_password_reset(
    user_id: UUID,
    _admin: Annotated[CurrentUser, Depends(require_super_admin())],
    _allowed: Annotated[CurrentUser, Depends(require_impersonation_allowed())],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse:
    await send_password_reset(session, user_id=user_id)
    return SuccessResponse()
