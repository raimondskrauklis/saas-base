# backend/app/core/config.py
"""Application settings — fail-fast on missing required env (no URL defaults in code)."""
from __future__ import annotations

import json
import os
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_DATABASE_FIELDS: dict[str, tuple[str, str]] = {
    "development": ("dev_database_url", "DEV_DATABASE_URL"),
    "test": ("test_database_url", "TEST_DATABASE_URL"),
    "staging": ("staging_database_url", "STAGING_DATABASE_URL"),
    "production": ("production_database_url", "PRODUCTION_DATABASE_URL"),
}

_ENV_DATABASE_READONLY_FIELDS: dict[str, tuple[str, str]] = {
    "development": ("dev_database_url_readonly", "DEV_DATABASE_URL_READONLY"),
    "test": ("test_database_url_readonly", "TEST_DATABASE_URL_READONLY"),
    "staging": ("staging_database_url_readonly", "STAGING_DATABASE_URL_READONLY"),
    "production": ("production_database_url_readonly", "PRODUCTION_DATABASE_URL_READONLY"),
}

_ALEMBIC_STAGE_ALIASES: dict[str, str] = {
    "dev": "development",
    "development": "development",
    "test": "test",
    "staging": "staging",
    "prod": "production",
    "production": "production",
}

_LEGACY_DATABASE_URL_MSG = (
    "DATABASE_URL is not used. Set DEV_DATABASE_URL, TEST_DATABASE_URL, "
    "STAGING_DATABASE_URL, or PRODUCTION_DATABASE_URL for ENVIRONMENT."
)


def canonicalize_environment(value: str) -> str:
    env = _ALEMBIC_STAGE_ALIASES.get(value.strip().lower())
    if env is None:
        allowed = ", ".join(sorted(_ENV_DATABASE_FIELDS))
        raise ValueError(f"ENVIRONMENT must be one of: {allowed} (got {value!r})")
    return env


def alembic_stage_from_x_arguments(x: dict[str, str]) -> str | None:
    """`alembic -x test=true` or `-x database=staging`. Default: ENVIRONMENT."""
    if x.get("test", "").lower() == "true":
        return "test"
    raw = (x.get("database") or "").strip()
    return raw or None


def database_url_for(settings: Settings, stage: str | None = None) -> str:
    """URL for ENVIRONMENT, or an Alembic `-x database=` / `-x test=true` override."""
    raw = (stage or settings.environment).strip().lower()
    env = _ALEMBIC_STAGE_ALIASES.get(raw)
    if env is None:
        allowed = ", ".join(sorted(_ENV_DATABASE_FIELDS))
        raise ValueError(f"database stage must be one of: {allowed} (got {stage!r})")
    field, env_name = _ENV_DATABASE_FIELDS[env]
    url = getattr(settings, field)
    if not url or not str(url).strip():
        raise ValueError(f"{env_name} is required when targeting {env}")
    return str(url).strip()


def database_url_readonly_for(settings: Settings, stage: str | None = None) -> str:
    """SELECT-only URL for Cursor / analysis. Not used by FastAPI or Alembic."""
    raw = (stage or settings.environment).strip().lower()
    env = _ALEMBIC_STAGE_ALIASES.get(raw)
    if env is None:
        allowed = ", ".join(sorted(_ENV_DATABASE_READONLY_FIELDS))
        raise ValueError(f"database stage must be one of: {allowed} (got {stage!r})")
    field, env_name = _ENV_DATABASE_READONLY_FIELDS[env]
    url = getattr(settings, field)
    if not url or not str(url).strip():
        raise ValueError(f"{env_name} is required for read-only access to {env}")
    return str(url).strip()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # Required — set in backend/.env (see .env.example)
    environment: str
    redis_url: str
    secret_key: str
    allowed_origins: str

    # Stage URLs — ENVIRONMENT selects the process bind (admin). Unused stages may be omitted.
    dev_database_url: str | None = None
    test_database_url: str | None = None
    staging_database_url: str | None = None
    production_database_url: str | None = None

    # Read-only — Cursor / analysis (SELECT). Not used by FastAPI or Alembic.
    dev_database_url_readonly: str | None = None
    test_database_url_readonly: str | None = None
    staging_database_url_readonly: str | None = None
    production_database_url_readonly: str | None = None

    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str
    # JWT `iss` when it differs from KEYCLOAK_URL (e.g. public auth host vs docker `keycloak:8080`)
    keycloak_issuer: str | None = None

    # One-time first deploy — remove from .env after super admin first login
    bootstrap_super_admin_email: str | None = None
    keycloak_webhook_secret: str | None = None

    # Registration — USER_REGISTRATION.md (open SaaS default)
    registration_require_admin_approval: bool = False
    registration_require_profile_form: bool = False

    # Security — comma-separated hosts for TrustedHostMiddleware (production).
    # Include the compose service name Keycloak uses (Host: backend).
    trusted_hosts: str = "localhost,127.0.0.1,backend"

    # Optional overrides (default to redis_url when unset)
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    # Operational — safe non-secret defaults
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"
    app_name: str = "App"
    app_version: str = "1.0.0"
    app_public_url: str | None = None
    keycloak_frontend_client_id: str = "app-web"

    # Pagination
    default_page_limit: int = 50
    max_page_limit: int = 100

    # Sentry — optional
    sentry_dsn: str | None = None
    sentry_release: str | None = None
    sentry_enable_in_test: bool = False
    sentry_send_default_pii: bool = False
    sentry_traces_sample_rate_debug: float = 1.0
    sentry_traces_sample_rate_prod: float = 0.1

    # Email — console local, mailgun production
    email_provider: str = "console"
    email_from: str | None = None
    email_from_name: str | None = None
    mailgun_api_key: str | None = None
    mailgun_domain: str | None = None
    mailgun_region: str = "eu"
    mailgun_webhook_signing_key: str | None = None

    # Stripe billing — disabled by default; set STRIPE_ENABLED=true with keys in production
    stripe_enabled: bool = False
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_pro: str | None = None
    stripe_checkout_success_url: str | None = None
    stripe_checkout_cancel_url: str | None = None

    # Data export — ACCOUNT_LIFECYCLE.md
    export_storage_path: str = "/tmp/app/exports"
    export_ttl_days: int = 7

    @property
    def keycloak_webhooks_enabled(self) -> bool:
        return bool(self.keycloak_webhook_secret and self.keycloak_webhook_secret.strip())

    @property
    def keycloak_token_issuer(self) -> str:
        """OIDC issuer (`iss`) for JWT validation — public URL when KEYCLOAK_URL is internal."""
        if self.keycloak_issuer:
            return self.keycloak_issuer.rstrip("/")
        base = self.keycloak_url.rstrip("/")
        return f"{base}/realms/{self.keycloak_realm}"

    @property
    def cors_origins(self) -> list[str]:
        raw = self.allowed_origins.strip()
        if raw.startswith("["):
            return json.loads(raw)
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @model_validator(mode="after")
    def require_database_url_for_environment(self) -> Self:
        if os.environ.get("DATABASE_URL", "").strip():
            raise ValueError(_LEGACY_DATABASE_URL_MSG)
        env = canonicalize_environment(self.environment)
        self.environment = env
        field, env_name = _ENV_DATABASE_FIELDS[env]
        url = getattr(self, field)
        if not url or not str(url).strip():
            raise ValueError(f"{env_name} is required when ENVIRONMENT={env}")
        return self

    @property
    def database_url(self) -> str:
        """Process bind — URL for the current ENVIRONMENT."""
        return database_url_for(self)


settings = Settings()
