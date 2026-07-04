from SmartApi import SmartConnect

from app.angel.client import AngelClient
from app.angel.exceptions import AngelAPIException


class AngelService:

    @staticmethod
    def get_ltp(
        exchange: str,
        symbol: str,
        token: str,
    ) -> dict:

        smart_api: SmartConnect = AngelClient.login()

        response = smart_api.ltpData(
            exchange=exchange,
            tradingsymbol=symbol,
            symboltoken=token,
        )

        if not response.get("status"):
            raise AngelAPIException(
                response.get(
                    "message",
                    "Unable to fetch LTP.",
                )
            )

        return response["data"]