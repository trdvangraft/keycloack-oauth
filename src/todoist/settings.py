from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    authorization_url: str = "http://localhost/auth/realms/todoist-realm/protocol/openid-connect/auth"
    token_url: str = "http://keycloak:8080/auth/realms/todoist-realm/protocol/openid-connect/token"
    server_url: str = "http://keycloak:8080/auth/"
    client_id: str = "todoist-app"
    realm: str = "todoist-realm"
    client_secret: str = "wFQEH8c2BAz9EqiCN8s7vK9sKXRsbaQ2"
    frontend_url: str = "http://localhost"


SETTINGS = Settings()