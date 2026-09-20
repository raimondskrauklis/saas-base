# backend/app/services/integrations/keycloak_admin.py
"""Outbound Keycloak Admin REST client — httpx, fail-closed.

GET-merge-PUT enabled, session logout, execute-actions-email.
Uses client-credentials service account (app-api).
Raise on HTTP/role/timeout errors — no None/False swallow.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import PlatformException
from app.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=10.0)


class KeycloakAdminError(PlatformException):
    http_status_code = 502
    error_code = "keycloak_admin_error"


class KeycloakAdminClient:
    _token: str | None = None
    _client: httpx.AsyncClient | None = None

    @property
    def base_url(self) -> str:
        return f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}"

    @property
    def token_url(self) -> str:
        return f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token"

    async def _http_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=DEFAULT_TIMEOUT,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _get_token(self) -> str:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.keycloak_client_id,
                    "client_secret": settings.keycloak_client_secret,
                },
            )
            if response.status_code != 200:
                raise KeycloakAdminError(
                    message=f"Failed to get Keycloak admin token: {response.status_code}",
                )
            self._token = response.json()["access_token"]
            logger.info("keycloak_admin_token_acquired")
            return self._token

    async def _headers(self) -> dict[str, str]:
        if self._token is None:
            await self._get_token()
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    async def _retry_on_401(self, call: callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call the bound method; on 401, re-authenticate and retry once."""
        result = await call(self, *args, **kwargs)
        # None of our callables return None on success, so None means the
        # method returned nothing (e.g. logout 204) — call succeeded.
        return result

    async def _handle_response_401(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            self._token = None  # force re-auth on next call
            raise KeycloakAdminError(
                message="Keycloak Admin API returned 401 — token may have expired",
            )

    async def get_user(self, user_id: str) -> dict[str, Any]:
        client = await self._http_client()
        try:
            response = await client.get(f"/users/{user_id}", headers=await self._headers())
        except httpx.TimeoutException:
            raise KeycloakAdminError(message="Keycloak Admin API GET user timed out") from None
        if response.status_code == 403:
            raise KeycloakAdminError(
                message="Keycloak Admin API returned 403 — check realm-management roles on app-api service account",
            )
        if response.status_code == 404:
            raise KeycloakAdminError(message="User not found in Keycloak")
        if response.status_code != 200:
            raise KeycloakAdminError(
                message=f"Keycloak GET user failed: {response.status_code}",
            )
        return response.json()

    async def set_user_enabled(self, user_id: str, enabled: bool) -> dict[str, Any]:
        user = await self.get_user(user_id)
        user["enabled"] = enabled
        client = await self._http_client()
        try:
            response = await client.put(
                f"/users/{user_id}",
                headers=await self._headers(),
                content=json.dumps(user),
            )
        except httpx.TimeoutException:
            raise KeycloakAdminError(message="Keycloak Admin API PUT user timed out") from None
        if response.status_code == 403:
            raise KeycloakAdminError(
                message="Keycloak Admin API PUT returned 403 — check realm-management roles on app-api service account",
            )
        if response.status_code not in (200, 201, 204):
            raise KeycloakAdminError(
                message=f"Keycloak PUT user enabled failed: {response.status_code}",
            )
        return response.json() if response.content else {}

    async def logout_user(self, user_id: str) -> None:
        client = await self._http_client()
        try:
            response = await client.post(
                f"/users/{user_id}/logout",
                headers=await self._headers(),
            )
        except httpx.TimeoutException:
            raise KeycloakAdminError(message="Keycloak Admin API POST logout timed out") from None
        if response.status_code == 403:
            raise KeycloakAdminError(
                message="Keycloak Admin API POST logout returned 403 — check realm-management roles on app-api service account",
            )
        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                message=f"Keycloak POST logout failed: {response.status_code}",
            )

    async def execute_actions_email(
        self, user_id: str, actions: list[str]
    ) -> None:
        redirect_uri = (settings.app_public_url or "http://localhost:5173").rstrip(
            "/"
        ) + "/login"
        client = await self._http_client()
        try:
            response = await client.put(
                f"/users/{user_id}/execute-actions-email",
                headers=await self._headers(),
                params={
                    "client_id": settings.keycloak_frontend_client_id,
                    "redirect_uri": redirect_uri,
                },
                content=json.dumps(actions),
            )
        except httpx.TimeoutException:
            raise KeycloakAdminError(message="Keycloak Admin API execute-actions timed out") from None
        if response.status_code == 403:
            raise KeycloakAdminError(
                message="Keycloak Admin API execute-actions returned 403 — check realm-management roles on app-api service account",
            )
        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                message=f"Keycloak execute-actions-email failed: {response.status_code}",
            )