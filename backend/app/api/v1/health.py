from fastapi import APIRouter

from app.core.response import success_response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health():
    return success_response(
        data={
            "status": "healthy"
        },
        message="Application is running",
    )