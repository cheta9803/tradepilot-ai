from SmartApi import SmartConnect

from app.core.config import settings


class SmartAPIClient:

    _client: SmartConnect | None = None

    @classmethod
    def get_client(cls) -> SmartConnect:

        if cls._client is None:

            cls._client = SmartConnect(
                api_key=settings.angel_api_key,
            )

        return cls._client


smart_api = SmartAPIClient.get_client()