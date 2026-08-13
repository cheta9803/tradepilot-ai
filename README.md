# TradePilot AI — 2026-08-14 trading-control update

Based on the latest backend and frontend ZIPs uploaded on 2026-08-13.

## Changes

1. 15m -> 5m -> 1m alignment remains the core decision flow.
2. A real completed-1m price-action trigger is now required:
   - BUY: bullish breakout OR bullish engulfing.
   - SELL: bearish breakdown OR bearish engulfing.
3. Consecutive-loss cooldown is implemented using completed trade history.
   - Default: 3 consecutive losses -> 30 minutes without new entries.
   - A profitable or break-even trade resets the streak.
4. Initial, break-even, and trailing stops now preserve their stop reason:
   - STOPLOSS
   - BREAKEVEN_STOP
   - TRAILING_STOP
5. P&L History renders Gross Loss explicitly with the loss/red class.
6. P&L History displays readable exit-reason labels.
7. Tests were extended for the new trigger, cooldown, and exit-reason behavior.

## Important

The current configuration already has a gross daily-loss limit of ₹2,000. Once today's gross realized loss reaches that limit, new trades remain blocked even if the scanner/dashboard shows opportunities.

These changes do not place or test live broker orders. They are intended to be installed and tested outside market hours first.

## Files

Backend: 14 complete files.
Frontend: 3 complete files.

The files are ready to copy over the corresponding paths in the project.
