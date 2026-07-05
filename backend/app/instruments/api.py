from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.instruments.schemas import InstrumentResponse
from app.instruments.service import InstrumentService

router = APIRouter(
    prefix="/instruments",
    tags=["Instruments"],
)


@router.get(
    "/search",
    response_model=list[InstrumentResponse],
)
def search_instruments(
    q: str = Query(
        ...,
        min_length=1,
        description="Search by symbol, trading symbol or token",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):

    return InstrumentService.search(
        db=db,
        query=q,
        limit=limit,
    )