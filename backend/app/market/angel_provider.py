from app.angel.service import AngelService


class AngelMarketProvider:

    def get_ltp(
        self,
        exchange: str,
        symbol: str,
        token: str,
    ):

        return AngelService.get_ltp(
            exchange=exchange,
            symbol=symbol,
            token=token,
        )