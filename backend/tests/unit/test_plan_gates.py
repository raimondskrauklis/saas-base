# backend/tests/unit/test_plan_gates.py
"""Plan feature gating — unknown features allowed; mapped features require plan."""
import uuid
from unittest.mock import AsyncMock

import pytest

from app.constants.enums import WorkspaceStatus
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.plan_gates import (
    PLAN_FEATURES,
    require_plan_feature,
    workspace_has_feature,
)
from app.models.workspaces import WorkspaceORM

EXAMPLE_FEATURE = "example.pro"


def _workspace(*, plan: str | None) -> WorkspaceORM:
    workspace = WorkspaceORM(
        slug="acme",
        name="Acme Corp",
        status=WorkspaceStatus.active,
        plan=plan,
    )
    workspace.id = uuid.uuid4()
    return workspace


def test_plan_features_has_no_installations_gate():
    assert "installations.create" not in PLAN_FEATURES


def test_unknown_feature_allowed_on_free():
    workspace = _workspace(plan=None)
    assert workspace_has_feature(workspace, "unknown.feature") is True


def test_workspace_has_feature_free_denied(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(PLAN_FEATURES, EXAMPLE_FEATURE, "pro")
    workspace = _workspace(plan=None)
    assert workspace_has_feature(workspace, EXAMPLE_FEATURE) is False


def test_workspace_has_feature_pro_allowed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(PLAN_FEATURES, EXAMPLE_FEATURE, "pro")
    workspace = _workspace(plan="pro")
    assert workspace_has_feature(workspace, EXAMPLE_FEATURE) is True


@pytest.mark.asyncio
async def test_require_plan_feature_raises_for_free_plan(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(PLAN_FEATURES, EXAMPLE_FEATURE, "pro")
    workspace_id = uuid.uuid4()
    workspace = _workspace(plan=None)
    workspace.id = workspace_id
    session = AsyncMock()
    session.get = AsyncMock(return_value=workspace)
    dependency = require_plan_feature(EXAMPLE_FEATURE)

    with pytest.raises(ForbiddenError) as exc:
        await dependency(workspace_id=workspace_id, session=session)

    assert exc.value.error_code == "plan_upgrade_required"
    assert exc.value.details == {
        "feature": EXAMPLE_FEATURE,
        "required_plan": "pro",
    }


@pytest.mark.asyncio
async def test_require_plan_feature_allows_pro_plan(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(PLAN_FEATURES, EXAMPLE_FEATURE, "pro")
    workspace_id = uuid.uuid4()
    workspace = _workspace(plan="pro")
    workspace.id = workspace_id
    session = AsyncMock()
    session.get = AsyncMock(return_value=workspace)
    dependency = require_plan_feature(EXAMPLE_FEATURE)

    await dependency(workspace_id=workspace_id, session=session)


@pytest.mark.asyncio
async def test_require_plan_feature_workspace_not_found():
    workspace_id = uuid.uuid4()
    session = AsyncMock()
    session.get = AsyncMock(return_value=None)
    dependency = require_plan_feature(EXAMPLE_FEATURE)

    with pytest.raises(NotFoundError):
        await dependency(workspace_id=workspace_id, session=session)
