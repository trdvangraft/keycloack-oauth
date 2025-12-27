import logging
from typing import Any, Callable, Coroutine

from fastapi import Depends, HTTPException, status

from keycloak import KeycloakOpenID

from todoist.settings import SETTINGS
from todoist.models import KeyCloakUser

from fastapi import Security
from fastapi.security import OAuth2AuthorizationCodeBearer

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=SETTINGS.authorization_url, # https://sso.example.com/auth/
    refreshUrl=SETTINGS.token_url,
    tokenUrl=SETTINGS.token_url, # https://sso.example.com/auth/realms/example-realm/protocol/openid-connect/token
)


# This actually does the auth checks
# client_secret_key is not mandatory if the client is public on keycloak
keycloak_openid = KeycloakOpenID(
    server_url=SETTINGS.server_url, # https://sso.example.com/auth/
    client_id=SETTINGS.client_id, # backend-client-id
    realm_name=SETTINGS.realm, # example-realm
    verify=False
)

async def get_current_user(token: str = Security(oauth2_scheme)) -> KeyCloakUser:
    logger.debug("Decoding Keycloak token")

    try:
        token_info = keycloak_openid.decode_token(
            token=token,
            validate=True,
        )
    except Exception as exc:
        logger.exception("Failed to decode/verify Keycloak token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    # Optionally call userinfo; this hits the userinfo endpoint
    try:
        userinfo = keycloak_openid.userinfo(token)
    except Exception:
        # Not critical; we can fall back to just token claims
        userinfo = {}

    print(token_info)
    print(token)
    # print(keycloak_openid.get_permissions(token=token))

    # ---- Map Keycloak roles → permissions ----
    # Realm roles
    realm_roles: list[str] = token_info.get("realm_access", {}).get("roles", []) or []
    # Client roles
    client_roles: list[str] = (
        token_info.get("resource_access", {})
        .get(SETTINGS.client_id, {})
        .get("roles", [])
        or []
    )
    permissions = list(set(realm_roles + client_roles))

    user = KeyCloakUser(
        sub=token_info.get("sub"),
        username=userinfo.get("preferred_username") or token_info.get("preferred_username"),
        email=userinfo.get("email") or token_info.get("email"),
        permissions=permissions,
    )

    logger.info("Authenticated Keycloak user %s with permissions %s", user.username, user.permissions)
    return user


def require_permissions(
    required_permissions: list[str],
) -> Callable[..., Coroutine[Any, Any, KeyCloakUser]]:
    logger.info("Setting up permission checker for: %s", required_permissions)

    async def checker(user: KeyCloakUser = Depends(get_current_user)) -> KeyCloakUser:
        logger.info("Checking user permissions: %s", user.permissions)
        logger.info("Required permissions: %s", required_permissions)

        user_permissions: list[str] = user.permissions or []
        missing_permissions: list[str] = [
            perm for perm in required_permissions if perm not in user_permissions
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing_permissions}",
            )

        return user

    return checker
