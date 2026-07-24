from threading import Lock

import pyotp
from SmartApi import SmartConnect

from app.angel.exceptions import AngelAPIException
from app.core.config import settings


class AngelClient:

    _client: SmartConnect | None = None
    _lock = Lock()

    @classmethod
    def login(cls) -> SmartConnect:

        if cls._client is not None:
            return cls._client

        with cls._lock:

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

            if (
                response is None
                or not response.get("status")
            ):
                raise AngelAPIException(
                    response.get(
                        "message",
                        "Angel One login failed.",
                    )
                    if response
                    else "Angel One login failed."
                )

            refresh_token = response["data"][
                "refreshToken"
            ]

            token_response = smart_api.generateToken(
                refresh_token,
            )

            if (
                token_response is None
                or not token_response.get("status")
            ):
                raise AngelAPIException(
                    "Unable to generate broker access token."
                )

            cls._client = smart_api

            return cls._client

    @classmethod
    def get_client(cls) -> SmartConnect:
        return cls.login()

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._client is not None

    @classmethod
    def reset(cls) -> None:
        cls._client = None