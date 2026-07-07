import threading

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from app.angel.client import AngelClient
from app.core.config import settings


class LiveClient:

    def __init__(self):
        self.smart_api = AngelClient.login()

        self.feed_token = self.smart_api.getfeedToken()

        self.client = SmartWebSocketV2(
            auth_token=self.feed_token,
            api_key=settings.angel_api_key,
            client_code=settings.angel_client_id,
            feed_token=self.feed_token,
        )

        self._thread: threading.Thread | None = None

    def connect(self):

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(
            target=self.client.connect,
            daemon=True,
        )

        self._thread.start()

    def close(self):
        self.client.close_connection()