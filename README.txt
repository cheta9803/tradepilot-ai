TradePilot AI - Live WebSocket Fix v2

Root cause found from live logs:
The watchdog was treating SmartWebSocketV2's internal pong timestamp as a hard health signal. That timestamp can remain stale while live market ticks continue arriving, causing TradePilot to force a reconnect roughly every 60 seconds.

Fix:
- Market ticks are now the authoritative market-hours feed-health signal.
- A stale SDK pong is retained for diagnostics but no longer forces reconnect by itself.
- Reconnect still occurs when no live ticks arrive past the configured timeout (with the first-tick grace period).
- Existing connection-generation and fresh-subscription protections remain unchanged.

Replace:
backend/app/live/client.py
backend/app/live/manager.py
backend/tests/live/test_live_client.py
backend/tests/live/test_live_manager.py
