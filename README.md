# TradePilot AI — Strategy Update — 14 Aug 2026

This patch is based on the latest backend/frontend ZIP uploaded on 14 Aug 2026.

## Changes

1. **Use 5m ATR for active-trade risk management**
   - The master 15m → 5m → 1m strategy already calculates the initial stop from 5m ATR.
   - Active trailing/breakeven logic now uses the same 5m risk timeframe instead of 1m ATR noise.

2. **Delay trailing-stop activation**
   - Trailing starts only after price moves at least **1.5 × 5m ATR** in the trade's favor.
   - Trailing distance remains **1.0 × 5m ATR**.
   - Break-even remains at **1.0 × 5m ATR**.
   - This is intended to reduce premature trailing-stop exits during normal intraday pullbacks.

3. **Fresh 1m trigger protection**
   - The 1m strategy now records the completed candle that produced the entry trigger.
   - A completed trade cannot immediately re-enter from the same trigger candle.
   - A genuinely new 1m trigger candle is required.

4. **15-minute symbol loss cooldown**
   - After a losing completed trade, the same symbol is blocked for 15 minutes.
   - This is separate from the existing account-wide 3-consecutive-loss / 30-minute cooldown.
   - A profitable or break-even latest trade does not trigger this symbol cooldown.

5. **Tests added/updated**
   - Trailing start threshold
   - 5m risk timeframe
   - Symbol loss cooldown
   - Latest closed trade lookup
   - Fresh 1m trigger propagation/consumption

## What is intentionally NOT changed

- The core 15m → 5m → 1m alignment requirement remains.
- The 70% minimum confidence remains.
- The 1m breakout / bullish-engulfing entry trigger remains.
- Risk/reward remains 1:2.
- Frontend strategy/UI files are not changed by this patch.

## Apply

Copy the files in this ZIP over the corresponding files in the backend project. Do not copy the ZIP's README over the repository README unless desired.

Then run from `backend`:

    python -m pytest -q
    git diff --check

This patch is intended for **paper trading** validation first. Do not enable live trading because of this change alone.
