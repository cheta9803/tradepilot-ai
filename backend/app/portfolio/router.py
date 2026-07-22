from fastapi import APIRouter

from app.portfolio.schemas import PortfolioResponse
from app.portfolio.service import PortfolioService

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get(
    "",
    response_model=PortfolioResponse,
)
def get_portfolio() -> PortfolioResponse:

    return PortfolioService.summary()