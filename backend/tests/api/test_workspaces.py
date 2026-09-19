# backend/tests/api/test_workspaces.py
"""HTTP contract — workspace list envelope and forbidden admin path."""
from __future__ import annotations

import pytest

from scripts.seed_test_data import SEED_USER_ID, SEED_WORKSPACE_ID


@pytest.mark.asyncio
async def test_workspace_members_list_envelope(async_client):
    response = await async_client.get(f"/api/v1/workspaces/{SEED_WORKSPACE_ID}/members")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "cursor" in data
    assert "has_next" in data["cursor"]
    assert isinstance(data["items"], list)
    assert any(item["user_id"] == str(SEED_USER_ID) for item in data["items"])


@pytest.mark.asyncio
async def test_admin_pending_users_forbidden_for_workspace_admin(async_client):
    response = await async_client.get("/api/v1/admin/users/pending")
    assert response.status_code == 403
    body = response.json()
    assert "error" in body
    assert "message" in body
