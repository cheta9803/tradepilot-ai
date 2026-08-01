from threading import Lock

from app.angel.provider import AngelMarketProvider


class MarketService:

    def __init__(self):

        self.provider = AngelMarketProvider()

        self._ticks: dict[str, dict] = {}

        self._lock = Lock()

    def get_history(
        self,
        symbol: str,
        timeframe: str = "5m",
        limit: int = 20,
    ):
        return self.provider.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    def update_tick(
        self,
        tick: dict,
    ) -> None:

        with self._lock:

            self._ticks[
                tick["symbol"]
            ] = tick

    def get_tick(
        self,
        symbol: str,
    ) -> dict | None:

        with self._lock:

            return self._ticks.get(
                symbol,
            )

    def get_all_ticks(
        self,
    ) -> dict[str, dict]:

        with self._lock:

            return dict(
                self._ticks,
            )

    def clear(
        self,
    ) -> None:

        with self._lock:

            self._ticks.clear()


market_service = MarketService()