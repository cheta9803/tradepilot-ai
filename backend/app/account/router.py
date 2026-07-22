from fastapi import APIRouter

from app.account.schemas import AccountResponse
from app.account.service import AccountService

router = APIRouter(
    prefix="/account",
    tags=["Account"],
)


@router.get(
    "",
    response_model=AccountResponse,
)
def get_account() -> AccountResponse:

    return AccountService.summary()