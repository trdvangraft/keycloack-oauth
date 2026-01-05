from pydantic import BaseModel


class KeyCloakUser(BaseModel):
    sub: str
    username: str | None = None
    email: str | None = None
    permissions: list[str] = []


class AuthConfig(BaseModel):
    """Public auth configuration for frontend - no secrets exposed."""
    authorization_url: str
    client_id: str
    redirect_uri: str


class TokenRequest(BaseModel):
    """Request to exchange authorization code for tokens."""
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    """Token response returned to frontend."""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""
    refresh_token: str
