from fastapi import WebSocket

from app.core.logger import logger


class WebSocketManager:

    def __init__(self):

        self.connections: list[WebSocket] = []

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:

        await websocket.accept()

        self.connections.append(
            websocket,
        )

        logger.info(
            "Frontend connected. Total=%d",
            len(self.connections),
        )

    def disconnect(
        self,
        websocket: WebSocket,
    ) -> None:

        if websocket in self.connections:

            self.connections.remove(
                websocket,
            )

        logger.info(
            "Frontend disconnected. Total=%d",
            len(self.connections),
        )

    async def broadcast(
        self,
        message: dict,
    ) -> None:

        disconnected: list[WebSocket] = []

        for connection in self.connections:

            try:

                await connection.send_json(
                    message,
                )

            except Exception:

                disconnected.append(
                    connection,
                )

        for connection in disconnected:

            self.disconnect(
                connection,
            )


websocket_manager = WebSocketManager()