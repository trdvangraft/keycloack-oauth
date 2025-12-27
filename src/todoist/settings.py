from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    authorization_url: str = "http://localhost:8080/realms/todoist-realm/protocol/openid-connect/auth"
    token_url: str = "http://localhost:8080/realms/todoist-realm/protocol/openid-connect/token"
    server_url: str = "http://keycloak_web:8080/todoist-realm"
    client_id: str = "todoist-app"
    realm: str = "	todoist-realm"
    client_secret: str = "Stz0zxQ9rFNWvllbmEaUkiiljVuHFUku"

SETTINGS = Settings()