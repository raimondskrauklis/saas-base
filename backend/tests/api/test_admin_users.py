# backend/tests/api/test_admin_users.py
"""HTTP contract — GET /api/v1/admin/users — P2."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_admin_users_list_401_unauthenticated(anonymous_client):
    response = await anonymous_client.get("/api/v1/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_users_list_403_non_super_admin(async_client):
    """Seeded user has platform_role=None → not super_admin → 403."""
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 403