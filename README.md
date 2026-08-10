# TradePilot backend history/live-indicator fix

This patch is based on the latest `app(20260810-051312).zip`.

## Changes
- Keep a 10-trading-day 1m warm-up instead of replacing history with only today's candles.
- Increase the 1m history cache to 4000 candles.
- Merge historical refresh data with existing cached candles.
- Build 5m/15m/30m/1h candles by timestamp buckets instead of list position, avoiding overnight/session-crossing candles.
- Recalculate indicators when cached indicators belong to an older candle, preventing stale indicators + today's LTP.
- Add the source candle timestamp to indicator cache values.
- Add a shared historical-request throttle and controlled Angel One rate-limit handling.
- Return HTTP 429 for `/market/history/{symbol}` when Angel historical data is rate-limited.

## Important
Do NOT commit this patch immediately.

After copying the files into the real backend, restart the backend and run the existing test suite first. Then verify INFY 5m and 15m during market hours.

Do not change `loadLtp()` or the WebSocket code as part of this patch.
