from pydantic import BaseModel


class InstrumentResponse(BaseModel):
    exchange: str
    symbol: str
    trading_symbol: str
    token: str
    instrument_type: str