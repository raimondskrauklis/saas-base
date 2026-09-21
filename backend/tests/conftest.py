# backend/tests/conftest.py
"""Pytest fixtures — unit tests mock the session; tests/api/ use TEST_DATABASE_URL."""
from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.constants.enums import AppRole, UserStatus
from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from scripts.seed_test_data import (
    SEED_EMAIL,
    SEED_KEYCLOAK_SUB,
    SEED_USER_ID,
    SEED_WORKSPACE_ID,
    require_test_database,
    upsert_l1_seed,
)


def _test_database_url() -> str | None:
    from app.core.config import settings

    return os.environ.get("TEST_DATABASE_URL") or settings.test_database_url


@pytest.fixture
def seed_current_user() -> CurrentUser:
    return CurrentUser(
        sub=SEED_KEYCLOAK_SUB,
        actor_user_id=SEED_USER_ID,
        email=SEED_EMAIL,
        workspace_id=SEED_WORKSPACE_ID,
        role=AppRole.admin,
        status=UserStatus.active,
    )


@pytest.fixture
async def db_session() -> AsyncSession:
    database_url = _test_database_url()
    if not database_url:
        pytest.skip("TEST_DATABASE_URL not configured")
    require_test_database(database_url)

    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await upsert_l1_seed(session)
        await session.commit()
        yield session
    await engine.dispose()


@pytest.fixture
async def async_client(db_session: AsyncSession, seed_current_user: CurrentUser):
    from app.main import app

    async def _override_get_db():
        yield db_session

    async def _override_get_current_user() -> CurrentUser:
        return seed_current_user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def anonymous_client():
    from app.main import app

    original = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original)
