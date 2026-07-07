from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.db import get_db
from app.users.models import User
from app.watchlist.live_schemas import WatchlistLiveResponse
from app.watchlist.schemas import WatchlistCreate
from app.watchlist.schemas import WatchlistResponse
from app.watchlist.service import WatchlistService

router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)


@router.post(
    "",
    response_model=WatchlistResponse,
    status_code=201,
)
def create_watchlist(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return WatchlistService.create(
            db=db,
            current_user=current_user,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[WatchlistResponse],
)
def list_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WatchlistService.list(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/live",
    response_model=list[WatchlistLiveResponse],
)
def list_live_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WatchlistService.list_live(
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/{watchlist_id}",
    status_code=204,
)
def delete_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        WatchlistService.delete(
            db=db,
            current_user=current_user,
            watchlist_id=watchlist_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )