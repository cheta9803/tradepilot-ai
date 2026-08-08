import threading
from enum import Enum

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from app.angel.client import AngelClient
from app.core.config import settings


class ConnectionState(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"


class LiveClient:

    def __init__(self):

        self.smart_api = None
        self.feed_token = None
        self.client = None

        self.state = ConnectionState.DISCONNECTED
        self._thread: threading.Thread | None = None

    def initialize(self):

        if self.client is not None:
            return

        self.smart_api = AngelClient.get_client()

        self.feed_token = self.smart_api.getfeedToken()

        self.client = SmartWebSocketV2(
            auth_token=self.feed_token,
            api_key=settings.angel_api_key,
            client_code=settings.angel_client_id,
            feed_token=self.feed_token,
        )

    def connect(self):

        if self.state in (
            ConnectionState.CONNECTING,
            ConnectionState.CONNECTED,
        ):
            return

        self.state = ConnectionState.CONNECTING

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

    def _run(self):

        try:
            self.client.connect()
        finally:
            self.state = ConnectionState.DISCONNECTED

    def mark_connected(self):
        self.state = ConnectionState.CONNECTED

    def mark_disconnected(self):
        self.state = ConnectionState.DISCONNECTED

    def close(self):

        self.mark_disconnected()

        if self.client is not None:
            self.client.close_connection()