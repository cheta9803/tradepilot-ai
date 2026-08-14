from app.core.config import settings
from app.strategy.entry_location import EntryLocationFilter


def _strategies(*, resistance_5m=None, resistance_15m=None, support_5m=None, support_15m=None):
    return {
        "15m": {
            "resistance": resistance_15m,
            "support": support_15m,
        },
        "5m": {
            "resistance": resistance_5m,
            "support": support_5m,
        },
        "1m": {},
    }


def test_buy_is_blocked_when_resistance_is_before_target():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = True

    try:
        result = EntryLocationFilter.evaluate(
            signal="BUY",
            entry=100.0,
            target=106.0,
            atr_5m=3.0,
            strategies=_strategies(resistance_5m=104.0),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["allowed"] is False
    assert result["timeframe"] == "5m"
    assert result["level"] == 104.0
    assert "too close" in result["reason"].lower()


def test_buy_is_allowed_when_resistance_leaves_target_room():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = True

    try:
        result = EntryLocationFilter.evaluate(
            signal="BUY",
            entry=100.0,
            target=106.0,
            atr_5m=3.0,
            strategies=_strategies(resistance_5m=107.0),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["allowed"] is True
    assert result["timeframe"] == "5m"
    assert result["level"] == 107.0


def test_nearest_resistance_is_used():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = True

    try:
        result = EntryLocationFilter.evaluate(
            signal="BUY",
            entry=100.0,
            target=104.0,
            atr_5m=2.0,
            strategies=_strategies(
                resistance_5m=110.0,
                resistance_15m=105.0,
            ),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["timeframe"] == "15m"
    assert result["level"] == 105.0
    assert result["allowed"] is True


def test_sell_is_blocked_when_support_is_before_target():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = True

    try:
        result = EntryLocationFilter.evaluate(
            signal="SELL",
            entry=100.0,
            target=94.0,
            atr_5m=3.0,
            strategies=_strategies(support_5m=96.0),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["allowed"] is False
    assert result["timeframe"] == "5m"
    assert result["level"] == 96.0


def test_no_overhead_level_does_not_block_trade():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = True

    try:
        result = EntryLocationFilter.evaluate(
            signal="BUY",
            entry=100.0,
            target=106.0,
            atr_5m=3.0,
            strategies=_strategies(
                resistance_5m=99.0,
                resistance_15m=98.0,
            ),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["allowed"] is True
    assert result["level"] is None


def test_filter_can_be_disabled():
    original = settings.entry_location_filter_enabled
    settings.entry_location_filter_enabled = False

    try:
        result = EntryLocationFilter.evaluate(
            signal="BUY",
            entry=100.0,
            target=106.0,
            atr_5m=3.0,
            strategies=_strategies(resistance_5m=101.0),
        )
    finally:
        settings.entry_location_filter_enabled = original

    assert result["allowed"] is True
    assert "disabled" in result["reason"].lower()