# backend/tests/unit/test_trusted_hosts.py
"""TrustedHostMiddleware on staging and production droplets."""
from unittest.mock import patch

from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.main import create_app


def _has_trusted_host(app) -> bool:
    return any(m.cls is TrustedHostMiddleware for m in app.user_middleware)


def test_trusted_host_enabled_for_staging_and_production():
    from app import main as main_mod

    for env in ("staging", "production"):
        with patch.object(main_mod.settings, "environment", env):
            with patch.object(main_mod.settings, "trusted_hosts", "app.example.com,backend"):
                assert _has_trusted_host(create_app())


def test_trusted_host_skipped_in_development():
    from app import main as main_mod

    with patch.object(main_mod.settings, "environment", "development"):
        assert not _has_trusted_host(create_app())
