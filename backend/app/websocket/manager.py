import asyncio

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logger import logger


class WebSocketManager:

    def __init__(self):

        self.connections: list[WebSocket] = []

        self.loop: asyncio.AbstractEventLoop | None = None

        logger.info(
            "WebSocketManager created id=%s",
            hex(id(self)),
        )

    def set_loop(
        self,
        loop: asyncio.AbstractEventLoop,
    ) -> None:

        self.loop = loop

        logger.info(
            "Event loop registered.",
        )

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:

        logger.info(
            "CONNECT manager=%s",
            hex(id(self)),
        )

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

        while websocket in self.connections:

            self.connections.remove(
                websocket,
            )

        logger.info(
            "Frontend disconnected. Total=%d",
            len(self.connections),
        )

    def broadcast_threadsafe(
        self,
        message: dict,
    ) -> None:

        if self.loop is None:
            return

        asyncio.run_coroutine_threadsafe(
            self.broadcast(message),
            self.loop,
        )

    async def broadcast(
        self,
        message: dict,
    ) -> None:

        disconnected: list[WebSocket] = []

        for index, connection in enumerate(list(self.connections)):

            logger.info(
                "Connection %d state=%s",
                index,
                connection.client_state,
            )

            if connection.client_state != WebSocketState.CONNECTED:

                disconnected.append(
                    connection,
                )

                continue

            try:

                await connection.send_json(
                    message,
                )

                logger.info(
                    "Successfully sent to connection %d",
                    index,
                )

            except Exception:

                logger.exception(
                    "Failed sending to connection %d",
                    index,
                )

                disconnected.append(
                    connection,
                )

        for connection in disconnected:

            self.disconnect(
                connection,
            )


websocket_manager = WebSocketManager()