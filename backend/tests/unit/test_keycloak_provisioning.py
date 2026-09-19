# backend/tests/unit/test_keycloak_provisioning.py
"""Keycloak → PostgreSQL user provisioning — USER_PROVISIONING P0."""
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.constants.enums import PlatformRole, UserStatus
from app.core.exceptions import ConflictError, UnauthorizedError
from app.models.users import UserORM
from app.services.keycloak_provisioning import (
    apply_keycloak_user_deleted,
    provision_user_from_keycloak,
)
from app.services.users import BOOTSTRAP_KEYCLOAK_PLACEHOLDER


class _PgUniqueViolation:
    pgcode = "23505"


class _Nested:
    def __init__(self, session: AsyncMock) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncMock:
        return self._session

    async def __aexit__(self, *args: object) -> None:
        return None


def _session_with_flush() -> AsyncMock:
    session = AsyncMock()
    session.flush = AsyncMock()
    session.begin_nested = lambda: _Nested(session)
    session.expunge = lambda _obj: None

    async def _refresh(obj: UserORM) -> None:
        if getattr(obj, "id", None) is None:
            obj.id = uuid.uuid4()

    session.refresh = AsyncMock(side_effect=_refresh)
    return session


@pytest.mark.asyncio
async def test_provision_requires_email_for_new_user():
    session = _session_with_flush()
    with patch(
        "app.services.keycloak_provisioning.get_user_by_keycloak_id",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with pytest.raises(UnauthorizedError) as exc_info:
            await provision_user_from_keycloak(
                session,
                sub="kc-1",
                email=None,
                email_verified=True,
            )
    assert exc_info.value.error_code == "provision_email_required"


@pytest.mark.asyncio
async def test_provision_update_profile_without_email_updates_name():
    session = _session_with_flush()
    existing = UserORM(
        keycloak_user_id="kc-1",
        email="user@example.com",
        full_name="Old Name",
        status=UserStatus.active,
    )
    existing.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=existing,
        ),
        patch(
            "app.services.keycloak_provisioning.activate_bootstrap_super_admin",
            new_callable=AsyncMock,
            return_value=existing,
        ),
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-1",
            email=None,
            email_verified=True,
            display_name="New Name",
        )
    assert user.full_name == "New Name"


@pytest.mark.asyncio
async def test_provision_mode_a_creates_active_user_with_workspace():
    session = _session_with_flush()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._find_bootstrap_seed",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._assert_email_available",
            new_callable=AsyncMock,
        ),
        patch(
            "app.services.keycloak_provisioning.activate_bootstrap_super_admin",
            new_callable=AsyncMock,
            side_effect=lambda _s, user, **_: user,
        ),
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-new",
            email="User@Example.com",
            email_verified=True,
            display_name="Test User",
        )

    assert user.email == "user@example.com"
    assert user.status == UserStatus.active
    assert session.add.call_count >= 2


@pytest.mark.asyncio
async def test_provision_email_conflict_on_create():
    session = _session_with_flush()
    other = UserORM(keycloak_user_id="kc-other", email="taken@example.com", status=UserStatus.active)
    other.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._find_bootstrap_seed",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning.get_user_by_email",
            new_callable=AsyncMock,
            return_value=other,
        ),
    ):
        with pytest.raises(ConflictError) as exc_info:
            await provision_user_from_keycloak(
                session,
                sub="kc-new",
                email="taken@example.com",
                email_verified=True,
            )
    assert exc_info.value.error_code == "identity_email_conflict"


@pytest.mark.asyncio
async def test_provision_create_unique_violation_returns_existing_sub():
    session = _session_with_flush()
    session.flush = AsyncMock(side_effect=IntegrityError("INSERT", {}, _PgUniqueViolation()))
    winner = UserORM(
        keycloak_user_id="kc-new",
        email="user@example.com",
        status=UserStatus.pending_profile,
    )
    winner.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            side_effect=[None, winner],
        ),
        patch(
            "app.services.keycloak_provisioning._find_bootstrap_seed",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._assert_email_available",
            new_callable=AsyncMock,
        ),
        patch(
            "app.services.keycloak_provisioning.maybe_auto_provision_user",
            new_callable=AsyncMock,
            return_value=winner,
        ),
        patch(
            "app.services.keycloak_provisioning.activate_bootstrap_super_admin",
            new_callable=AsyncMock,
            return_value=winner,
        ),
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-new",
            email="user@example.com",
            email_verified=True,
        )
    assert user is winner


@pytest.mark.asyncio
async def test_provision_create_unique_violation_email_conflict():
    session = _session_with_flush()
    session.flush = AsyncMock(side_effect=IntegrityError("INSERT", {}, _PgUniqueViolation()))
    other = UserORM(
        keycloak_user_id="kc-other",
        email="taken@example.com",
        status=UserStatus.active,
    )
    other.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._find_bootstrap_seed",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._assert_email_available",
            new_callable=AsyncMock,
        ),
        patch(
            "app.services.keycloak_provisioning.get_user_by_email",
            new_callable=AsyncMock,
            return_value=other,
        ),
    ):
        with pytest.raises(ConflictError) as exc_info:
            await provision_user_from_keycloak(
                session,
                sub="kc-new",
                email="taken@example.com",
                email_verified=True,
            )
    assert exc_info.value.error_code == "identity_email_conflict"


@pytest.mark.asyncio
async def test_provision_links_bootstrap_seed_by_email():
    session = _session_with_flush()
    seeded = UserORM(
        keycloak_user_id=BOOTSTRAP_KEYCLOAK_PLACEHOLDER,
        email="admin@example.com",
        status=UserStatus.pending_activation,
        platform_role=PlatformRole.super_admin,
    )
    seeded.id = uuid.uuid4()
    activated = UserORM(
        keycloak_user_id="kc-admin",
        email="admin@example.com",
        status=UserStatus.active,
        platform_role=PlatformRole.super_admin,
    )
    activated.id = seeded.id
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.services.keycloak_provisioning._find_bootstrap_seed",
            new_callable=AsyncMock,
            return_value=seeded,
        ),
        patch(
            "app.services.keycloak_provisioning.activate_bootstrap_super_admin",
            new_callable=AsyncMock,
            return_value=activated,
        ) as activate,
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-admin",
            email="admin@example.com",
            email_verified=True,
        )
    activate.assert_awaited_once()
    assert user.status == UserStatus.active


@pytest.mark.asyncio
async def test_provision_idempotent_for_existing_sub():
    session = _session_with_flush()
    existing = UserORM(keycloak_user_id="kc-1", email="user@example.com", status=UserStatus.active)
    existing.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=existing,
        ),
        patch(
            "app.services.keycloak_provisioning._sync_user_email",
            new_callable=AsyncMock,
        ) as sync_email,
        patch(
            "app.services.keycloak_provisioning.maybe_auto_provision_user",
            new_callable=AsyncMock,
            return_value=existing,
        ),
        patch(
            "app.services.keycloak_provisioning.activate_bootstrap_super_admin",
            new_callable=AsyncMock,
            return_value=existing,
        ),
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-1",
            email="user@example.com",
            email_verified=True,
        )
    sync_email.assert_awaited_once()
    assert user is existing


@pytest.mark.asyncio
async def test_provision_email_update_conflict_on_existing_sub():
    session = _session_with_flush()
    existing = UserORM(keycloak_user_id="kc-1", email="old@example.com", status=UserStatus.active)
    existing.id = uuid.uuid4()
    other = UserORM(keycloak_user_id="kc-2", email="new@example.com", status=UserStatus.active)
    other.id = uuid.uuid4()
    with (
        patch(
            "app.services.keycloak_provisioning.get_user_by_keycloak_id",
            new_callable=AsyncMock,
            return_value=existing,
        ),
        patch(
            "app.services.keycloak_provisioning.get_user_by_email",
            new_callable=AsyncMock,
            return_value=other,
        ),
    ):
        with pytest.raises(ConflictError) as exc_info:
            await provision_user_from_keycloak(
                session,
                sub="kc-1",
                email="new@example.com",
                email_verified=True,
            )
    assert exc_info.value.error_code == "identity_email_conflict"


@pytest.mark.asyncio
async def test_provisioned_user_can_accept_invitation():
    """Invitee must exist in PG (provision) before accept_invitation."""
    from app.constants.enums import AppRole, InvitationStatus
    from app.models.invitations import WorkspaceInvitationORM
    from app.models.workspace_memberships import WorkspaceMembershipORM
    from app.services.invitations import accept_invitation

    session = AsyncMock()
    session.flush = AsyncMock()
    workspace_id = uuid.uuid4()
    user = UserORM(
        keycloak_user_id="kc-invitee",
        email="invitee@example.com",
        status=UserStatus.active,
    )
    user.id = uuid.uuid4()

    invitation = WorkspaceInvitationORM(
        workspace_id=workspace_id,
        email="invitee@example.com",
        role=AppRole.viewer,
        token="invite-token",
        status=InvitationStatus.pending,
        expires_at=datetime.now(UTC) + timedelta(days=1),
        invited_by_user_id=uuid.uuid4(),
    )

    session.scalar = AsyncMock(side_effect=[invitation, None])

    membership = await accept_invitation(session, token="invite-token", user=user)

    assert isinstance(membership, WorkspaceMembershipORM)
    assert membership.user_id == user.id
    assert membership.workspace_id == workspace_id
    assert invitation.status == InvitationStatus.accepted


@pytest.mark.asyncio
async def test_apply_keycloak_user_deleted_anonymizes_and_drops_memberships():
    session = _session_with_flush()
    session.execute = AsyncMock()
    user = UserORM(
        keycloak_user_id="kc-1",
        email="user@example.com",
        full_name="Test User",
        status=UserStatus.active,
    )
    user.id = uuid.uuid4()
    with patch(
        "app.services.keycloak_provisioning.get_user_by_keycloak_id",
        new_callable=AsyncMock,
        return_value=user,
    ):
        result = await apply_keycloak_user_deleted(session, sub="kc-1")

    assert result is user
    assert user.status == UserStatus.deleted
    assert user.email == f"deleted+{user.id}@app.invalid"
    assert user.full_name is None
    assert user.keycloak_user_id == "kc-1"
    session.execute.assert_awaited()


@pytest.mark.asyncio
async def test_provision_does_not_revive_deleted_user():
    session = _session_with_flush()
    deleted = UserORM(
        keycloak_user_id="kc-1",
        email="deleted+old@app.invalid",
        full_name=None,
        status=UserStatus.deleted,
    )
    deleted.id = uuid.uuid4()
    with patch(
        "app.services.keycloak_provisioning.get_user_by_keycloak_id",
        new_callable=AsyncMock,
        return_value=deleted,
    ):
        user = await provision_user_from_keycloak(
            session,
            sub="kc-1",
            email="user@example.com",
            email_verified=True,
            display_name="Revived",
        )
    assert user is deleted
    assert user.status == UserStatus.deleted
    assert user.email == "deleted+old@app.invalid"
    assert user.full_name is None
