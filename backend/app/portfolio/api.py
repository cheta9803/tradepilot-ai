from fastapi import APIRouter
from dataclasses import asdict

from app.portfolio.service import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get("")
def portfolio_summary():

    return asdict(
        PortfolioService.summary()
    )