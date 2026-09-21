# backend/app/schemas/admin.py
"""Platform admin API contracts — W5."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.constants.enums import PlatformRole, UserStatus, WorkspaceStatus
from app.schemas.audit import AuditListItem


class AdminWorkspaceListItem(BaseModel):
    id: UUID
    name: str
    slug: str
    status: WorkspaceStatus
    plan: str | None
    member_count: int
    created_at: datetime


class AdminWorkspaceDetail(BaseModel):
    id: UUID
    name: str
    slug: str
    status: WorkspaceStatus
    plan: str | None
    member_count: int
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime


class AdminKpisResponse(BaseModel):
    workspaces_total: int
    workspaces_active: int
    workspaces_suspended: int
    workspaces_deleted: int
    users_active: int
    users_pending_approval: int
    users_suspended: int


class AdminUserListItem(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    status: UserStatus
    platform_role: PlatformRole | None
    created_at: datetime


class AdminWorkspaceMembershipOut(BaseModel):
    workspace_id: UUID
    workspace_name: str
    role: str  # WorkspaceRole


class AdminUserDetail(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    status: UserStatus
    platform_role: PlatformRole | None
    impersonate_allowed: bool
    memberships: list[AdminWorkspaceMembershipOut]
    created_at: datetime
    updated_at: datetime


class AdminSettingsResponse(BaseModel):
    registration_require_admin_approval: bool
    registration_require_profile_form: bool


class PlatformAuditListItem(AuditListItem):
    workspace_id: UUID | None
