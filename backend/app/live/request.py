from pydantic import BaseModel


class SubscribeRequest(BaseModel):
    exchange: str
    token: str