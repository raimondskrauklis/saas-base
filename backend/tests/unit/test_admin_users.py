# backend/tests/unit/test_admin_users.py
"""Platform admin user directory + lifecycle mutations - P2/P3."""
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.constants.enums import PlatformRole, UserStatus
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.users import UserORM
from app.models.workspace_memberships import WorkspaceMembershipORM
from app.schemas.admin import AdminUserDetail, AdminWorkspaceMembershipOut
from app.services.admin_users import (
    approve_user,
    dual_write_user_enabled,
    get_admin_user_detail,
    list_admin_users,
    reactivate_user,
    reject_user,
    send_password_reset,
    suspend_user,
)
from app.services.integrations.keycloak_admin import KeycloakAdminError


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
        "keycloak_user_id": "kc-test-1",
        "email": "user@example.com",
        "full_name": "Test User",
        "status": UserStatus.active,
        "platform_role": None,
        "created_at": datetime(2026, 9, 20, tzinfo=UTC),
        "updated_at": datetime(2026, 9, 20, tzinfo=UTC),
    }
    kw.update(overrides)
    return UserORM(**kw)


# --- list + detail (P2) ---


@pytest.mark.asyncio
async def test_list_admin_users_returns_page(session: AsyncMock):
    user1 = _make_user(id=uuid4(), email="a@example.com")
    user2 = _make_user(id=uuid4(), email="b@example.com")
    from app.core.pagination import CursorParams

    session.execute = AsyncMock(return_value=_Result([(user1,), (user2,)]))
    page = await list_admin_users(session, params=CursorParams(limit=20, cursor=None))
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


@pytest.mark.asyncio
async def test_get_admin_user_detail_returns_user(session: AsyncMock):
    user = _make_user()
    session.get = AsyncMock(return_value=user)
    wm = WorkspaceMembershipORM(user_id=user.id, workspace_id=uuid4(), role="owner")
    session.execute = AsyncMock(return_value=_Result([(wm, "My WS")]))

    detail = await get_admin_user_detail(session, user_id=user.id)
    assert isinstance(detail, AdminUserDetail)
    assert detail.email == "user@example.com"
    assert detail.platform_role is None
    assert len(detail.memberships) == 1
    assert detail.memberships[0].workspace_name == "My WS"
    assert detail.impersonate_allowed is True


@pytest.mark.asyncio
async def test_get_admin_user_detail_not_found(session: AsyncMock):
    session.get = AsyncMock(return_value=None)
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
    wm = WorkspaceMembershipORM(user_id=user.id, workspace_id=uuid4(), role="member")
    session.execute = AsyncMock(return_value=_Result([(wm, "Team WS")]))
    detail = await get_admin_user_detail(session, user_id=user.id)
    assert len(detail.memberships) == 1
    assert isinstance(detail.memberships[0], AdminWorkspaceMembershipOut)
    assert detail.memberships[0].role == "member"


# --- dual_write (P3.1) ---


DUAL_PATCH_PATH = "app.services.admin_users._make_admin_client"


@pytest.mark.asyncio
async def test_dual_write_helper_raise_no_commit(session: AsyncMock):
    user = _make_user()
    mock_kc = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock(
        side_effect=KeycloakAdminError(message="fail")
    )

    with (
        patch(DUAL_PATCH_PATH, return_value=mock_kc),
        pytest.raises(KeycloakAdminError),
    ):
        async with dual_write_user_enabled(
            session, user=user, target_enabled=False, logout=False
        ):
            user.status = UserStatus.suspended
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_dual_write_commit_failure_restores_kc(session: AsyncMock):
    user = _make_user()
    mock_kc = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock()
    session.commit = AsyncMock(side_effect=RuntimeError("db fail"))

    with (
        patch(DUAL_PATCH_PATH, return_value=mock_kc),
        pytest.raises(RuntimeError),
    ):
        async with dual_write_user_enabled(
            session, user=user, target_enabled=False, logout=False
        ):
            user.status = UserStatus.suspended

    # Should have called set_user_enabled twice: first to disable, then to re-enable
    assert mock_kc.set_user_enabled.call_count == 2
    # Second call restores: enabled=True
    mock_kc.set_user_enabled.assert_any_call(user.keycloak_user_id, enabled=True)


# --- suspend / reactivate (P3.2) ---


@pytest.mark.asyncio
async def test_suspend_user_success(session: AsyncMock):
    user = _make_user(status=UserStatus.active)
    session.scalar = AsyncMock(return_value=user)  # _get_user_for_update
    mock_kc = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock()
    mock_kc.logout_user = AsyncMock()

    with patch(DUAL_PATCH_PATH, return_value=mock_kc):
        result = await suspend_user(session, user_id=user.id, actor_user_id=uuid4())
    assert result.status == UserStatus.suspended
    mock_kc.set_user_enabled.assert_called_with(user.keycloak_user_id, enabled=False)
    mock_kc.logout_user.assert_called_with(user.keycloak_user_id)


@pytest.mark.asyncio
async def test_suspend_self_blocked(session: AsyncMock):
    user_id = uuid4()
    with pytest.raises(ForbiddenError):
        await suspend_user(session, user_id=user_id, actor_user_id=user_id)


@pytest.mark.asyncio
async def test_suspend_last_super_admin_blocked(session: AsyncMock):
    user = _make_user(
        status=UserStatus.active, platform_role=PlatformRole.super_admin,
    )
    session.scalar = AsyncMock(return_value=user)
    # _count_active_super_admins: first call is user fetch (scalar), second is count
    # UserORM.scalar returns user, then func.count returns 1
    session.scalar = AsyncMock(side_effect=[user, 1])

    with pytest.raises(ForbiddenError):
        await suspend_user(session, user_id=user.id, actor_user_id=uuid4())


@pytest.mark.asyncio
async def test_reactivate_user_success(session: AsyncMock):
    user = _make_user(status=UserStatus.suspended)
    session.scalar = AsyncMock(return_value=user)
    mock_kc = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock()

    with patch(DUAL_PATCH_PATH, return_value=mock_kc):
        result = await reactivate_user(session, user_id=user.id, actor_user_id=uuid4())
    assert result.status == UserStatus.active
    mock_kc.set_user_enabled.assert_called_with(user.keycloak_user_id, enabled=True)


@pytest.mark.asyncio
async def test_reactivate_non_suspended_raises(session: AsyncMock):
    user = _make_user(status=UserStatus.active)
    session.scalar = AsyncMock(return_value=user)
    with pytest.raises(ValidationError):
        await reactivate_user(session, user_id=user.id, actor_user_id=uuid4())


# --- approve / reject (P3.3) ---


@pytest.mark.asyncio
async def test_approve_user_success(session: AsyncMock):
    user = _make_user(status=UserStatus.pending_approval)
    session.scalar = AsyncMock(return_value=user)
    mock_kc = AsyncMock()
    mock_kc.get_user = AsyncMock(return_value={"emailVerified": True})
    mock_kc.set_user_enabled = AsyncMock()

    async def fake_activate(ssn, u, *, name):
        u.status = UserStatus.active

    with (
        patch(DUAL_PATCH_PATH, return_value=mock_kc),
        patch("app.services.admin_users.activate_user_with_workspace", side_effect=fake_activate),
    ):
        result = await approve_user(session, user_id=user.id, actor_user_id=uuid4())
    assert result.status == UserStatus.active


@pytest.mark.asyncio
async def test_approve_unverified_email_sends_verify(session: AsyncMock):
    user = _make_user(status=UserStatus.pending_approval)
    session.scalar = AsyncMock(return_value=user)
    mock_kc = AsyncMock()
    mock_kc.get_user = AsyncMock(return_value={"emailVerified": False})
    mock_kc.execute_actions_email = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock()

    async def fake_activate(ssn, u, *, name):
        u.status = UserStatus.active

    with (
        patch(DUAL_PATCH_PATH, return_value=mock_kc),
        patch("app.services.admin_users.activate_user_with_workspace", side_effect=fake_activate),
    ):
        await approve_user(session, user_id=user.id, actor_user_id=uuid4())
    mock_kc.execute_actions_email.assert_called_with(user.keycloak_user_id, ["VERIFY_EMAIL"])




@pytest.mark.asyncio
async def test_reject_user_success(session: AsyncMock):
    user = _make_user(status=UserStatus.pending_approval)
    session.scalar = AsyncMock(return_value=user)
    mock_kc = AsyncMock()
    mock_kc.set_user_enabled = AsyncMock()
    mock_kc.logout_user = AsyncMock()

    with patch(DUAL_PATCH_PATH, return_value=mock_kc):
        result = await reject_user(session, user_id=user.id, actor_user_id=uuid4())
    assert result.status == UserStatus.rejected
    mock_kc.logout_user.assert_called_with(user.keycloak_user_id)


# --- send password reset (P3.4) ---


@pytest.mark.asyncio
async def test_send_password_reset_success(session: AsyncMock):
    user = _make_user()
    session.get = AsyncMock(return_value=user)
    mock_kc = AsyncMock()
    mock_kc.execute_actions_email = AsyncMock()

    with patch(DUAL_PATCH_PATH, return_value=mock_kc):
        await send_password_reset(session, user_id=user.id)
    mock_kc.execute_actions_email.assert_called_with(
        user.keycloak_user_id, ["UPDATE_PASSWORD"]
    )


@pytest.mark.asyncio
async def test_send_password_reset_not_found(session: AsyncMock):
    session.get = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await send_password_reset(session, user_id=uuid4())
