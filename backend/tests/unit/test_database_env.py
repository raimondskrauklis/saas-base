# backend/tests/unit/test_database_env.py
"""ENVIRONMENT selects the process database URL."""
import pytest
from pydantic import ValidationError

from app.core.config import (
    Settings,
    alembic_stage_from_x_arguments,
    database_url_for,
    database_url_readonly_for,
)

_BASE = {
    "redis_url": "redis://localhost:6379/0",
    "secret_key": "test",
    "allowed_origins": "http://localhost:5173",
    "keycloak_url": "http://localhost:8080",
    "keycloak_realm": "app",
    "keycloak_client_id": "app-api",
    "keycloak_client_secret": "secret",
}

_STAGE_URL_KEYS = (
    "DEV_DATABASE_URL",
    "TEST_DATABASE_URL",
    "STAGING_DATABASE_URL",
    "PRODUCTION_DATABASE_URL",
    "DEV_DATABASE_URL_READONLY",
    "TEST_DATABASE_URL_READONLY",
    "STAGING_DATABASE_URL_READONLY",
    "PRODUCTION_DATABASE_URL_READONLY",
    "DATABASE_URL",
)


@pytest.fixture(autouse=True)
def _clear_stage_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _STAGE_URL_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_development_binds_dev_database_url():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
    )
    assert settings.database_url.endswith("/saas_base_dev")


def test_test_binds_test_database_url():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="test",
        test_database_url="postgresql+asyncpg://localhost/saas_base_test",
    )
    assert settings.database_url.endswith("/saas_base_test")


def test_staging_binds_staging_database_url():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="staging",
        staging_database_url="postgresql+asyncpg://localhost/saas_base_staging",
    )
    assert settings.database_url.endswith("/saas_base_staging")


def test_production_binds_production_database_url():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="production",
        production_database_url="postgresql+asyncpg://localhost/saas_base_prod",
    )
    assert settings.database_url.endswith("/saas_base_prod")


def test_missing_url_for_environment_fails():
    with pytest.raises(ValidationError, match="DEV_DATABASE_URL"):
        Settings(**_BASE, _env_file=None, environment="development")


def test_unknown_environment_fails():
    with pytest.raises(ValidationError, match="ENVIRONMENT must be one of"):
        Settings(
            **_BASE,
            _env_file=None,
            environment="local",
            dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
        )


def test_environment_alias_dev_is_rejected():
    with pytest.raises(ValidationError, match="ENVIRONMENT must be one of"):
        Settings(
            **_BASE,
            _env_file=None,
            environment="dev",
            dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
        )


def test_unknown_env_key_is_rejected():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Settings(
            **_BASE,
            _env_file=None,
            environment="development",
            dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
            github_app_id="leftover",
        )


def test_legacy_database_url_env_fails(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/legacy")
    with pytest.raises(ValidationError, match="DATABASE_URL is not used"):
        Settings(
            **_BASE,
            _env_file=None,
            environment="development",
            dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
        )


def test_alembic_x_test_true_selects_test():
    assert alembic_stage_from_x_arguments({"test": "true"}) == "test"


def test_alembic_x_database_staging_selects_staging():
    assert alembic_stage_from_x_arguments({"database": "staging"}) == "staging"


def test_alembic_default_uses_environment():
    assert alembic_stage_from_x_arguments({}) is None


def test_database_url_for_alembic_override_does_not_require_environment_match():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
        staging_database_url="postgresql+asyncpg://localhost/saas_base_staging",
    )
    assert database_url_for(settings, "staging").endswith("/saas_base_staging")
    assert database_url_for(settings, "dev").endswith("/saas_base_dev")


def test_database_url_for_missing_stage_url_fails():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
    )
    with pytest.raises(ValueError, match="STAGING_DATABASE_URL"):
        database_url_for(settings, "staging")


def test_readonly_url_optional_at_boot():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
    )
    assert settings.dev_database_url_readonly is None


def test_database_url_readonly_for_stage():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
        staging_database_url_readonly="postgresql+asyncpg://readonly@localhost/saas_base_staging",
        production_database_url_readonly="postgresql+asyncpg://readonly@localhost/saas_base_prod",
    )
    assert database_url_readonly_for(settings, "staging").endswith("/saas_base_staging")
    assert database_url_readonly_for(settings, "production").endswith("/saas_base_prod")


def test_database_url_readonly_for_missing_fails():
    settings = Settings(
        **_BASE,
        _env_file=None,
        environment="development",
        dev_database_url="postgresql+asyncpg://localhost/saas_base_dev",
    )
    with pytest.raises(ValueError, match="STAGING_DATABASE_URL_READONLY"):
        database_url_readonly_for(settings, "staging")
