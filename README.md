# TradePilot Strategy Hardening v2.1

Overlay patch for TradePilot after Strategy Hardening v1/v2.

## Fixes in v2.1

1. **Restore explicit RSI extreme rejection**
   - A BUY at RSI >= 70 is forced to HOLD even if other indicators produce a 4/5 bullish majority.
   - A SELL at RSI <= 30 is forced to HOLD for the same reason.
   - This fixes `test_strategy_rejects_overbought_buy`.

2. **Protect the 5m setup timeframe**
   - Keep the public per-timeframe floors at 15m=65%, 5m=65%, 1m=70%.
   - Add an explicit executable 5m setup floor of 70%.
   - A 69% 5m setup therefore returns WAIT, even when 15m/1m confidence is strong.
   - This fixes `test_low_confidence_means_wait` without changing the published hardening constants.

3. V2 fixes remain included:
   - Support/resistance excludes the current trigger candle.
   - Weighted MTF confidence remains 70%.
   - No-chase guard: 1.0 ATR normally, 1.25 ATR for confirmed breakouts.
   - Existing risk, cooldown, daily trade cap, VWAP, Supertrend and entry-location protections remain intact.

## Apply safely

1. Back up the current backend.
2. Extract this ZIP over the backend root, replacing only the files in this overlay.
3. Keep `.env`, database and runtime environment unchanged.
4. Run `python -m pytest -q`. Expected result: the two regressions reported after v2 should be resolved.
5. Restart the backend.
6. Test during tomorrow's market hours in paper trading.

Do not enable live trading based on this patch.
