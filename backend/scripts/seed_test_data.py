# backend/scripts/seed_test_data.py
"""L1 HTTP-smoke seed — TEST_DATABASE_URL only. Idempotent upsert (fixed UUIDs)."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import UUID

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.constants.enums import AppRole, UserStatus, WorkspaceStatus  # noqa: E402
from app.models.users import UserORM  # noqa: E402
from app.models.workspace_memberships import WorkspaceMembershipORM  # noqa: E402
from app.models.workspaces import WorkspaceORM  # noqa: E402

SEED_USER_ID = UUID("aaaaaaaa-bbbb-4ccc-8ddd-000000000001")
SEED_WORKSPACE_ID = UUID("aaaaaaaa-bbbb-4ccc-8ddd-000000000002")
SEED_MEMBERSHIP_ID = UUID("aaaaaaaa-bbbb-4ccc-8ddd-000000000003")
SEED_EMAIL = "seed@example.com"
SEED_KEYCLOAK_SUB = "seed-test-user"
SEED_WORKSPACE_SLUG = "seed-workspace"


def test_database_url() -> str:
    from app.core.config import settings

    url = os.environ.get("TEST_DATABASE_URL") or settings.test_database_url
    if not url or not str(url).strip():
        raise SystemExit("TEST_DATABASE_URL is required")
    return str(url).strip()


def database_name(url: str) -> str:
    parsed = urlparse(url.replace("postgresql+asyncpg://", "postgresql://", 1))
    return unquote(parsed.path.lstrip("/")).split("?")[0]


def require_test_database(url: str) -> None:
    name = database_name(url)
    if "test" not in name.lower():
        raise SystemExit(f"refusing to seed non-test database {name!r}")


async def upsert_l1_seed(session: AsyncSession) -> None:
    user = await session.get(UserORM, SEED_USER_ID)
    if user is None:
        user = UserORM(id=SEED_USER_ID)
        session.add(user)
    user.keycloak_user_id = SEED_KEYCLOAK_SUB
    user.email = SEED_EMAIL
    user.full_name = "Seed User"
    user.status = UserStatus.active
    user.platform_role = None
    user.locale = "en"
    user.timezone = "UTC"

    workspace = await session.get(WorkspaceORM, SEED_WORKSPACE_ID)
    if workspace is None:
        workspace = WorkspaceORM(id=SEED_WORKSPACE_ID)
        session.add(workspace)
    workspace.slug = SEED_WORKSPACE_SLUG
    workspace.name = "Seed Workspace"
    workspace.status = WorkspaceStatus.active
    workspace.plan = None

    membership = await session.get(WorkspaceMembershipORM, SEED_MEMBERSHIP_ID)
    if membership is None:
        existing = await session.scalar(
            select(WorkspaceMembershipORM).where(
                WorkspaceMembershipORM.user_id == SEED_USER_ID,
                WorkspaceMembershipORM.workspace_id == SEED_WORKSPACE_ID,
            )
        )
        membership = existing or WorkspaceMembershipORM(id=SEED_MEMBERSHIP_ID)
        if existing is None:
            session.add(membership)
    membership.user_id = SEED_USER_ID
    membership.workspace_id = SEED_WORKSPACE_ID
    membership.role = AppRole.admin

    await session.flush()


async def main() -> None:
    url = test_database_url()
    require_test_database(url)
    engine = create_async_engine(url, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await upsert_l1_seed(session)
        await session.commit()
    await engine.dispose()
    print(f"L1 seed upserted on {database_name(url)}")


if __name__ == "__main__":
    asyncio.run(main())
