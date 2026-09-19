# backend/alembic/versions/2026_09_19_2000_0012_workspace_memberships_updated_at.py
"""workspace_memberships.updated_at — TimestampedModel."""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "2026_09_19_2000_0012_workspace_memberships_updated_at"
down_revision = "2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workspace_memberships",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("workspace_memberships", "updated_at")
