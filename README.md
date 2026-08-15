# TradePilot AI — Live Feed Reliability Update

This update strengthens the Angel One market-data WebSocket lifecycle.

## Changes

- Supervises the Angel WebSocket in a dedicated reconnect loop.
- Recreates the SmartWebSocketV2 object after disconnects.
- Uses exponential reconnect backoff (5s → 10s → 20s → 40s → 60s max by default).
- Disables the SDK's internal retry so TradePilot owns reconnect state.
- Re-subscribes the required instruments through the existing `on_open` flow.
- Adds heartbeat watchdog: stale heartbeat forces a reconnect.
- Tracks connection, last tick, last pong, reconnect attempts and last error.
- Adds `GET /api/v1/live/health/status` for live-feed diagnostics.
- Adds unit tests for connection health and reconnect supervision.

## Configuration

New settings in `backend/app/core/config.py`:

- `LIVE_WS_RECONNECT_INITIAL_SECONDS=5`
- `LIVE_WS_RECONNECT_MAX_SECONDS=60`
- `LIVE_WS_HEARTBEAT_TIMEOUT_SECONDS=45`

Do not add broker credentials to source control.

## Verification after applying

Run:

```bash
cd backend
python -m pytest -q
python -m pytest tests/live/test_client.py -q
git diff --check
```

When the server is running:

```bash
curl -s http://127.0.0.1:8000/api/v1/live/health/status
```

During a live market session, the important fields are:

- `state`
- `last_tick_age_seconds`
- `last_pong_age_seconds`
- `reconnect_attempts`
- `subscribed_tokens`
- `last_error`
