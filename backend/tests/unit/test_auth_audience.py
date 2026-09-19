# backend/tests/unit/test_auth_audience.py
"""JWT audience / azp allowlist — AUTH.md."""
from unittest.mock import patch

import pytest

from app.core.auth import _validate_audience, token_client_allowlist
from app.core.exceptions import UnauthorizedError


def test_token_client_allowlist_includes_api_and_frontend():
    with (
        patch("app.core.auth.settings.keycloak_client_id", "app-api"),
        patch("app.core.auth.settings.keycloak_frontend_client_id", "app-web"),
    ):
        assert token_client_allowlist() == frozenset({"app-api", "app-web"})


def test_validate_audience_accepts_known_azp():
    with (
        patch("app.core.auth.settings.keycloak_client_id", "app-api"),
        patch("app.core.auth.settings.keycloak_frontend_client_id", "app-web"),
    ):
        _validate_audience({"azp": "app-web", "aud": "app-api"})


def test_validate_audience_rejects_unknown_azp():
    with (
        patch("app.core.auth.settings.keycloak_client_id", "app-api"),
        patch("app.core.auth.settings.keycloak_frontend_client_id", "app-web"),
    ):
        with pytest.raises(UnauthorizedError, match="authorized party"):
            _validate_audience({"azp": "evil-client", "aud": "app-api"})
