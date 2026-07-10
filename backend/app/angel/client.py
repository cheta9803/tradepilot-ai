from SmartApi import SmartConnect
import pyotp

from app.core.config import settings
from app.angel.exceptions import AngelAPIException


class AngelClient:

    _client: SmartConnect | None = None

    @classmethod
    def login(cls) -> SmartConnect:
        """
        Returns a shared authenticated SmartConnect
        instance.
        """

        if cls._client is not None:
            return cls._client

        smart_api = SmartConnect(
            api_key=settings.angel_api_key,
        )

        totp = pyotp.TOTP(
            settings.angel_totp_secret,
        ).now()

        response = smart_api.generateSession(
            settings.angel_client_id,
            settings.angel_pin,
            totp,
        )

        if not response.get("status"):
            raise AngelAPIException(
                response.get(
                    "message",
                    "Angel One login failed.",
                )
            )

        refresh_token = response["data"]["refreshToken"]

        smart_api.generateToken(
            refresh_token,
        )

        cls._client = smart_api

        return cls._client