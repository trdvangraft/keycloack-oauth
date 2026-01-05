import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from todoist.auth import require_permissions
from todoist.models import (
    KeyCloakUser,
    AuthConfig,
    TokenRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from todoist.settings import SETTINGS

class EnrollPermissions:
    TOKEN = "enroll"

class AnalyticsPermissions:
    ANALTYICS_VIEWER = "analytics:read"
    ANALYTICS_EDITOR = "analytics:write"


logger = logging.getLogger(__name__)

router = APIRouter()

CURRENT_VIEW_STATISTICS = {

}

@router.get("/user", response_model=KeyCloakUser)
async def get_user(user: KeyCloakUser = Depends(
        require_permissions(required_permissions=[])
    ),
) -> KeyCloakUser:
    """
    Returns the authenticated user's information extracted from the token.
    The token is validated by the backend, and claims/permissions are returned.
    """
    return user

@router.get("/analytics")
async def get_view_anlytics(user: KeyCloakUser = Depends(
    require_permissions(required_permissions=[AnalyticsPermissions.ANALTYICS_VIEWER])
)) -> dict:
    return {
        "score": CURRENT_VIEW_STATISTICS.get(user.sub, 0)
    }

@router.put("/analytics")
async def put_view_analytics(user: KeyCloakUser = Depends(
    require_permissions(required_permissions=[AnalyticsPermissions.ANALYTICS_EDITOR])
)) -> dict:
    CURRENT_VIEW_STATISTICS[user.sub] = CURRENT_VIEW_STATISTICS.get(user.sub, 0) + 1
    return {
        "score": CURRENT_VIEW_STATISTICS.get(user.sub, 0)
    }


@router.get("/config/auth", response_model=AuthConfig)
async def get_auth_config() -> AuthConfig:
    """
    Public endpoint that exposes OAuth configuration for frontend.
    """
    redirect_uri = f"{SETTINGS.frontend_url}/callback"
    return AuthConfig(
        authorization_url=SETTINGS.authorization_url,
        client_id=SETTINGS.client_id,
        redirect_uri=redirect_uri,
    )


@router.post("/auth/token", response_model=TokenResponse)
async def exchange_token(request: TokenRequest) -> TokenResponse:
    """
    Exchange authorization code for tokens (confidential client flow).
    The client secret is used server-side - never exposed to frontend.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SETTINGS.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": request.code,
                    "redirect_uri": request.redirect_uri,
                    "client_id": SETTINGS.client_id,
                    "client_secret": SETTINGS.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to exchange authorization code",
                )

            token_data = response.json()
            return TokenResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in", 300),
            )

        except httpx.RequestError as e:
            logger.exception("Error communicating with Keycloak")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            ) from e


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh an access token using the refresh token.
    """
    async with httpx.AsyncClient() as client:
        try:
            print(request)
            response = await client.post(
                SETTINGS.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": request.refresh_token,
                    "client_id": SETTINGS.client_id,
                    "client_secret": SETTINGS.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to refresh token",
                )

            token_data = response.json()
            return TokenResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_in=token_data.get("expires_in", 300),
            )

        except httpx.RequestError as e:
            logger.exception("Error communicating with Keycloak")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            ) from e