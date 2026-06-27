from pydantic import BaseModel


class RiskParameters(BaseModel):
    capital: float

    risk_percent: float

    reward_ratio: float