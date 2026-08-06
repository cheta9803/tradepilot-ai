from fastapi import APIRouter

from app.ai.service import AIService

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.get("/top")
def top_ai():

    return AIService.top_opportunities()