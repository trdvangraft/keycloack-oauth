from pydantic import BaseModel

class KeyCloakUser(BaseModel):
    sub: str
    username: str | None = None
    email: str | None = None
    permissions: list[str] = []
