from datetime import datetime, timedelta

from app.risk.limits import RiskLimits
from app.trades.cache import TradeCache


def test_no_trades_returns_false():

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: []
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original


def test_loss_below_limit_returns_false():

    today = datetime.now().isoformat()

    trades = [
        {
            "closed_at": today,
            "pnl": -500.0,
        },
        {
            "closed_at": today,
            "pnl": -700.0,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original


def test_loss_above_limit_returns_true():

    today = datetime.now().isoformat()

    trades = [
        {
            "closed_at": today,
            "pnl": -1000.0,
        },
        {
            "closed_at": today,
            "pnl": -1500.0,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is True

    finally:

        TradeCache.get_all = original


def test_yesterday_loss_is_ignored():

    yesterday = (
        datetime.now() - timedelta(days=1)
    ).isoformat()

    trades = [
        {
            "closed_at": yesterday,
            "pnl": -5000.0,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original


def test_profit_is_ignored():

    today = datetime.now().isoformat()

    trades = [
        {
            "closed_at": today,
            "pnl": 5000.0,
        },
        {
            "closed_at": today,
            "pnl": 2500.0,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original


def test_invalid_closed_at_is_ignored():

    trades = [
        {
            "closed_at": "invalid-date",
            "pnl": -10000.0,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original


def test_none_pnl_is_ignored():

    today = datetime.now().isoformat()

    trades = [
        {
            "closed_at": today,
            "pnl": None,
        },
    ]

    original = TradeCache.get_all

    TradeCache.get_all = classmethod(
        lambda cls: trades
    )

    try:

        assert RiskLimits.daily_loss_reached() is False

    finally:

        TradeCache.get_all = original