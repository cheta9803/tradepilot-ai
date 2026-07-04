from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    feed_token: str