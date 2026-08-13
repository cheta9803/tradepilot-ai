from datetime import datetime, timedelta

from app.risk.limits import RiskLimits
from app.trades.history_repository import TradeHistoryRepository
from app.core.config import settings


def test_no_trades_returns_false():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: 0.0)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is False
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_loss_below_limit_returns_false():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: 1200.0)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is False
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_loss_above_limit_returns_true():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: 2500.0)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is True
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_loss_exactly_at_limit_returns_true():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    limit = 2000.0

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: limit)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is True
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_profit_does_not_reduce_gross_loss():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: 1500.0)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is False
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_large_gross_loss_triggers_limit():

    original = (
        TradeHistoryRepository.get_today_gross_loss
    )

    TradeHistoryRepository.get_today_gross_loss = (
        classmethod(lambda cls: 5000.0)
    )

    try:

        assert (
            RiskLimits.daily_loss_reached()
            is True
        )

    finally:

        TradeHistoryRepository.get_today_gross_loss = (
            original
        )


def test_three_consecutive_losses_start_cooldown():

    original = TradeHistoryRepository.get_today_loss_streak
    original_minutes = settings.cooldown_minutes
    original_losses = settings.cooldown_after_losses

    TradeHistoryRepository.get_today_loss_streak = classmethod(
        lambda cls: (3, datetime.now())
    )
    settings.cooldown_after_losses = 3
    settings.cooldown_minutes = 30

    try:
        assert RiskLimits.loss_cooldown_reached() is True
    finally:
        TradeHistoryRepository.get_today_loss_streak = original
        settings.cooldown_minutes = original_minutes
        settings.cooldown_after_losses = original_losses


def test_profit_breaks_loss_streak():

    original = TradeHistoryRepository.get_today_loss_streak

    TradeHistoryRepository.get_today_loss_streak = classmethod(
        lambda cls: (0, None)
    )

    try:
        assert RiskLimits.loss_cooldown_reached() is False
    finally:
        TradeHistoryRepository.get_today_loss_streak = original


def test_expired_loss_cooldown_allows_trade():

    original = TradeHistoryRepository.get_today_loss_streak
    original_minutes = settings.cooldown_minutes
    original_losses = settings.cooldown_after_losses

    TradeHistoryRepository.get_today_loss_streak = classmethod(
        lambda cls: (
            3,
            datetime.now() - timedelta(minutes=31),
        )
    )
    settings.cooldown_after_losses = 3
    settings.cooldown_minutes = 30

    try:
        assert RiskLimits.loss_cooldown_reached() is False
    finally:
        TradeHistoryRepository.get_today_loss_streak = original
        settings.cooldown_minutes = original_minutes
        settings.cooldown_after_losses = original_losses
