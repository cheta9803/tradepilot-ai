import json
from dataclasses import asdict
from datetime import datetime

from app.db.redis import redis_client
from app.scanner.models import ScannerResult


class ScannerCache:

    PREFIX = "scanner"

    TOP_KEY = "top"

    @classmethod
    def _symbol_key(
        cls,
        symbol: str,
    ) -> str:

        return (
            f"{cls.PREFIX}:{symbol}"
        )

    @classmethod
    def save(
        cls,
        result: ScannerResult,
    ) -> None:

        data = asdict(
            result,
        )

        data["updated_at"] = (
            result.updated_at.isoformat()
        )

        redis_client.set(
            cls._symbol_key(
                result.symbol,
            ),
            json.dumps(
                data,
            ),
        )

    @classmethod
    def get(
        cls,
        symbol: str,
    ) -> dict | None:

        value = redis_client.get(
            cls._symbol_key(
                symbol,
            )
        )

        if value is None:
            return None

        return json.loads(
            value,
        )

    @classmethod
    def save_top(
        cls,
        results: list[ScannerResult],
    ) -> None:

        data = []

        for result in results:

            item = asdict(
                result,
            )

            item["updated_at"] = (
                result.updated_at.isoformat()
            )

            data.append(
                item,
            )

        redis_client.set(
            f"{cls.PREFIX}:{cls.TOP_KEY}",
            json.dumps(
                data,
            ),
        )

    @classmethod
    def get_top(
        cls,
    ) -> list[dict]:

        value = redis_client.get(
            f"{cls.PREFIX}:{cls.TOP_KEY}",
        )

        if value is None:
            return []

        return json.loads(
            value,
        )