from importlib.metadata import version
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from todoist.routes import router

from todoist.settings import SETTINGS

def create_app():
    current_version = version("todoist")
    app = FastAPI(
        version=current_version, 
        swagger_ui_init_oauth = {
            "clientId": SETTINGS.client_id, 
            "appName": "Todoist app", 
            "usePkceWithAuthorizationCodeGrant": False, 
            "scopes": "openid profile",

        }
    )

    # Allow requests from the browser (CORS settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*"
        ],  # Or specify ["http://localhost:8082"] for tighter security
        allow_credentials=True,
        allow_methods=["*"],  # Or ["POST", "GET", "OPTIONS"]
        allow_headers=["*"],
    )

    app.include_router(router)
    return app
