from app.strategy.execution_eligibility import TradeExecutionEligibility


def test_market_closed_blocks_execution(monkeypatch):
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.MarketSession.can_enter_trade",
        lambda: False,
    )

    result = TradeExecutionEligibility.evaluate(
        exchange="NSE",
        token="123",
        trigger_candle_timestamp=None,
    )

    assert result["execution_ready"] is False
    assert "Market is closed" in result["execution_block_reason"]


def test_existing_trade_blocks_execution(monkeypatch):
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.MarketSession.can_enter_trade",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.TradeCache.get",
        lambda **kwargs: {"state": "BUY_ACTIVE"},
    )

    result = TradeExecutionEligibility.evaluate(
        exchange="NSE",
        token="123",
        trigger_candle_timestamp=None,
    )

    assert result["execution_ready"] is False
    assert "existing 1m trade" in result["execution_block_reason"]


def test_risk_block_reason_is_exposed(monkeypatch):
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.MarketSession.can_enter_trade",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.TradeCache.get",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.PreTradeRiskEngine.evaluate",
        lambda **kwargs: (False, "Consecutive-loss cooldown active. New trades are blocked."),
    )

    result = TradeExecutionEligibility.evaluate(
        exchange="NSE",
        token="123",
        trigger_candle_timestamp=None,
    )

    assert result["execution_ready"] is False
    assert "cooldown" in result["execution_block_reason"].lower()


def test_execution_is_ready_when_all_gates_pass(monkeypatch):
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.MarketSession.can_enter_trade",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.TradeCache.get",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "app.strategy.execution_eligibility.PreTradeRiskEngine.evaluate",
        lambda **kwargs: (True, None),
    )

    result = TradeExecutionEligibility.evaluate(
        exchange="NSE",
        token="123",
        trigger_candle_timestamp=None,
    )

    assert result == {
        "execution_ready": True,
        "execution_block_reason": None,
    }
