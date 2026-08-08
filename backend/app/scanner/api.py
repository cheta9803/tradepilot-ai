from fastapi import APIRouter
from fastapi import Query

from app.scanner.service import ScannerService


router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)


@router.get("/top")
def top_scanner(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
):

    return ScannerService.get_top(
        limit=limit,
        refresh=True,
    )