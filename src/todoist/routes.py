import logging

from fastapi import APIRouter, Security, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from todoist.auth import get_current_user
from todoist.models import KeyCloakUser
from todoist.auth import require_permissions

class EnrollPermissions:
    TOKEN = "enroll"

class AnalyticsPermissions:
    ANALTYICS_VIEWER = "analytics_viewer"
    ANALYTICS_EDITOR = "analytics_editor"


logger = logging.getLogger(__name__)

router = APIRouter()

CURRENT_VIEW_STATISTICS = {

}

@router.get("/user")
async def get_user(user: KeyCloakUser = Depends(
        require_permissions(required_permissions=[])
    ),
) -> dict:
    return {"message": f"User info endpoint {user}"}

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