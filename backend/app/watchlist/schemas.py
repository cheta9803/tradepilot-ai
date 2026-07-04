from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class WatchlistCreate(BaseModel):
    symbol: str
    exchange: str


class WatchlistResponse(BaseModel):
    id: int
    symbol: str
    exchange: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )