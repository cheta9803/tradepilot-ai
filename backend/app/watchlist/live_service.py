from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.watchlist.models import Watchlist


class WatchlistLiveService:

    @staticmethod
    def get_live_data(
        watchlist: Watchlist,
    ) -> dict:

        instrument = InstrumentCache.get_by_symbol(
            exchange=watchlist.exchange,
            symbol=watchlist.symbol,
        )

        if instrument is None:
            return {
                "id": watchlist.id,
                "exchange": watchlist.exchange,
                "symbol": watchlist.symbol,
                "token": "",
                "trading_symbol": "",
                "ltp": None,
                "change": None,
                "change_percent": None,
                "open": None,
                "high": None,
                "low": None,
                "close": None,
                "volume": None,
                "timestamp": None,
            }

        live = LiveCache.get(
            instrument.token,
        )

        if live is None:
            return {
                "id": watchlist.id,
                "exchange": instrument.exchange,
                "symbol": instrument.symbol,
                "token": instrument.token,
                "trading_symbol": instrument.trading_symbol,
                "ltp": None,
                "change": None,
                "change_percent": None,
                "open": None,
                "high": None,
                "low": None,
                "close": None,
                "volume": None,
                "timestamp": None,
            }

        close = live.get("close", 0)

        ltp = live.get("ltp", 0)

        change = ltp - close

        change_percent = (
            (change / close) * 100
            if close
            else 0
        )

        return {
            "id": watchlist.id,
            "exchange": instrument.exchange,
            "symbol": instrument.symbol,
            "token": instrument.token,
            "trading_symbol": instrument.trading_symbol,
            "ltp": ltp,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "open": live.get("open"),
            "high": live.get("high"),
            "low": live.get("low"),
            "close": close,
            "volume": live.get("volume"),
            "timestamp": live.get("timestamp"),
        }