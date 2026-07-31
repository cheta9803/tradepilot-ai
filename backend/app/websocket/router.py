from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.websocket.manager import websocket_manager
from app.websocket.schemas import BroadcastTickRequest

router = APIRouter(
    tags=["WebSocket"],
)


@router.websocket("/ws/market")
async def market_socket(
    websocket: WebSocket,
):

    await websocket_manager.connect(
        websocket,
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        websocket_manager.disconnect(
            websocket,
        )


@router.post("/api/v1/websocket/test")
async def broadcast_test(
    request: BroadcastTickRequest,
):

    await websocket_manager.broadcast(
        request.model_dump(),
    )

    return {
        "message": "Broadcast successful.",
    }