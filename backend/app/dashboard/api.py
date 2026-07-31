from dataclasses import asdict

from fastapi import APIRouter

from app.dashboard.service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
async def get_dashboard():

    return asdict(
        DashboardService.get()
    )