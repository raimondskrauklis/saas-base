# backend/tests/api/test_me.py
"""HTTP contract — GET /api/v1/me."""
from __future__ import annotations

import pytest

from scripts.seed_test_data import SEED_EMAIL, SEED_USER_ID, SEED_WORKSPACE_ID


@pytest.mark.asyncio
async def test_me_returns_seeded_active_user(async_client):
    response = await async_client.get("/api/v1/me")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["id"] == str(SEED_USER_ID)
    assert data["email"] == SEED_EMAIL
    assert data["status"] == "active"
    assert data["workspace_id"] == str(SEED_WORKSPACE_ID)


@pytest.mark.asyncio
async def test_me_unauthorized_without_auth(anonymous_client):
    response = await anonymous_client.get("/api/v1/me")
    assert response.status_code == 401
    body = response.json()
    assert "error" in body
    assert "message" in body
