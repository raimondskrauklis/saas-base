# backend/tests/unit/test_admin_users.py
"""Platform admin user directory — P2."""
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.constants.enums import PlatformRole, UserStatus
from app.models.users import UserORM
from app.models.workspace_memberships import WorkspaceMembershipORM
from app.schemas.admin import AdminUserDetail, AdminWorkspaceMembershipOut
from app.services.admin_users import get_admin_user_detail, list_admin_users


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def all(self) -> list[object]:
        return self._rows


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


def _make_user(**overrides: object) -> UserORM:
    kw: dict[str, object] = {
        "id": uuid4(),
        "email": "user@example.com",
        "full_name": "Test User",
        "status": UserStatus.active,
        "platform_role": None,
        "created_at": datetime(2026, 9, 20, tzinfo=UTC),
        "updated_at": datetime(2026, 9, 20, tzinfo=UTC),
    }
    kw.update(overrides)
    return UserORM(**kw)


# ——— list ———


@pytest.mark.asyncio
async def test_list_admin_users_returns_page(session: AsyncMock):
    user1 = _make_user(id=uuid4(), email="a@example.com")
    user2 = _make_user(id=uuid4(), email="b@example.com")

    from app.core.pagination import CursorParams

    session.execute = AsyncMock(return_value=_Result([(user1,), (user2,)]))
    page = await list_admin_users(
        session, params=CursorParams(limit=20, cursor=None),
    )
    assert len(page.items) == 2
    assert page.items[0].email == "a@example.com"


@pytest.mark.asyncio
async def test_list_admin_users_status_filter(session: AsyncMock):
    session.execute = AsyncMock(return_value=_Result([]))
    from app.core.pagination import CursorParams

    await list_admin_users(
        session, params=CursorParams(limit=20, cursor=None), status=UserStatus.suspended,
    )
    stmt = str(session.execute.call_args[0][0])
    assert "status" in stmt


@pytest.mark.asyncio
async def test_list_admin_users_search(session: AsyncMock):
    session.execute = AsyncMock(return_value=_Result([]))
    from app.core.pagination import CursorParams

    await list_admin_users(
        session, params=CursorParams(limit=20, cursor=None), search="test",
    )
    stmt = str(session.execute.call_args[0][0])
    assert "%test%" in stmt or "full_name" in stmt


# ——— detail ———


@pytest.mark.asyncio
async def test_get_admin_user_detail_returns_user(session: AsyncMock):
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    wm = WorkspaceMembershipORM(
        user_id=user.id,
        workspace_id=uuid4(),
        role="owner",
    )
    session.execute = AsyncMock(return_value=_Result([(wm, "My WS")]))

    detail = await get_admin_user_detail(session, user_id=user.id)
    assert isinstance(detail, AdminUserDetail)
    assert detail.email == "user@example.com"
    assert detail.platform_role is None
    assert len(detail.memberships) == 1
    assert detail.memberships[0].workspace_name == "My WS"
    assert detail.impersonate_allowed is True    # regular + active


@pytest.mark.asyncio
async def test_get_admin_user_detail_not_found(session: AsyncMock):
    session.get = AsyncMock(return_value=None)
    from app.core.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await get_admin_user_detail(session, user_id=uuid4())


@pytest.mark.asyncio
async def test_impersonate_not_allowed_for_super_admin(session: AsyncMock):
    user = _make_user(platform_role=PlatformRole.super_admin, status=UserStatus.active)
    session.get = AsyncMock(return_value=user)
    session.execute = AsyncMock(return_value=_Result([]))

    detail = await get_admin_user_detail(session, user_id=user.id)
    assert detail.impersonate_allowed is False


@pytest.mark.asyncio
async def test_impersonate_not_allowed_for_suspended(session: AsyncMock):
    user = _make_user(status=UserStatus.suspended)
    session.get = AsyncMock(return_value=user)
    session.execute = AsyncMock(return_value=_Result([]))

    detail = await get_admin_user_detail(session, user_id=user.id)
    assert detail.impersonate_allowed is False


@pytest.mark.asyncio
async def test_detail_includes_memberships(session: AsyncMock):
    user = _make_user()
    session.get = AsyncMock(return_value=user)

    wm = WorkspaceMembershipORM(
        user_id=user.id, workspace_id=uuid4(), role="member",
    )
    session.execute = AsyncMock(return_value=_Result([(wm, "Team WS")]))

    detail = await get_admin_user_detail(session, user_id=user.id)
    assert len(detail.memberships) == 1
    assert isinstance(detail.memberships[0], AdminWorkspaceMembershipOut)
    assert detail.memberships[0].role == "member"