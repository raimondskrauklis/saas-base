# backend/tests/unit/test_keycloak_admin.py
"""Keycloak Admin REST client — mocked httpx, fail-closed contract."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.integrations.keycloak_admin import (
    KeycloakAdminClient,
    KeycloakAdminError,
)


@pytest.fixture
def admin_client() -> KeycloakAdminClient:
    return KeycloakAdminClient()


# ——— token ———


@pytest.mark.asyncio
async def test_get_token_success(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"access_token": "tok-1"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.return_value = mock_response
        token = await admin_client._get_token()
        assert token == "tok-1"


@pytest.mark.asyncio
async def test_get_token_401_raises(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 401

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as post:
        post.return_value = mock_response
        with pytest.raises(KeycloakAdminError):
            await admin_client._get_token()


# ——— enabled ———


@pytest.mark.asyncio
async def test_set_user_enabled(admin_client: KeycloakAdminClient):
    get_response = AsyncMock()
    get_response.status_code = 200
    get_response.json = lambda: {"id": "kc-1", "enabled": True}

    put_response = AsyncMock()
    put_response.status_code = 204
    put_response.content = b""

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.get = AsyncMock(return_value=get_response)
        client.put = AsyncMock(return_value=put_response)

        result = await admin_client.set_user_enabled("kc-1", enabled=False)
        assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_set_user_enabled_403_raises(admin_client: KeycloakAdminClient):
    get_response = AsyncMock()
    get_response.status_code = 200
    get_response.json = lambda: {"id": "kc-1", "enabled": True}

    put_response = AsyncMock()
    put_response.status_code = 403

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.get = AsyncMock(return_value=get_response)
        client.put = AsyncMock(return_value=put_response)

        with pytest.raises(KeycloakAdminError):
            await admin_client.set_user_enabled("kc-1", enabled=False)


# ——— logout ———


@pytest.mark.asyncio
async def test_logout_user(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 204

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.post = AsyncMock(return_value=mock_response)

        await admin_client.logout_user("kc-1")
        client.post.assert_called_once()


@pytest.mark.asyncio
async def test_logout_user_403_raises(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 403

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(KeycloakAdminError):
            await admin_client.logout_user("kc-1")


# ——— execute-actions ———


@pytest.mark.asyncio
async def test_execute_actions_email(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 204

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.put = AsyncMock(return_value=mock_response)

        await admin_client.execute_actions_email("kc-1", ["UPDATE_PASSWORD"])
        client.put.assert_called_once()


@pytest.mark.asyncio
async def test_execute_actions_email_403_raises(admin_client: KeycloakAdminClient):
    mock_response = AsyncMock()
    mock_response.status_code = 403

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.put = AsyncMock(return_value=mock_response)

        with pytest.raises(KeycloakAdminError):
            await admin_client.execute_actions_email("kc-1", ["UPDATE_PASSWORD"])


# ——— fail-closed contract ———


@pytest.mark.asyncio
async def test_get_user_timeout_raises(admin_client: KeycloakAdminClient):
    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with pytest.raises(KeycloakAdminError):
            await admin_client.get_user("kc-1")


@pytest.mark.asyncio
async def test_put_5xx_raises(admin_client: KeycloakAdminClient):
    get_response = AsyncMock()
    get_response.status_code = 200
    get_response.json = lambda: {"id": "kc-1", "enabled": True}

    put_response = AsyncMock()
    put_response.status_code = 500

    with (
        patch.object(admin_client, "_get_token", new_callable=AsyncMock) as tok,
        patch.object(admin_client, "_http_client", new_callable=AsyncMock),
    ):
        tok.return_value = "tok-1"
        client = await admin_client._http_client()
        client.get = AsyncMock(return_value=get_response)
        client.put = AsyncMock(return_value=put_response)

        with pytest.raises(KeycloakAdminError):
            await admin_client.set_user_enabled("kc-1", enabled=False)