from types import SimpleNamespace

from app.live.client import ConnectionState, LiveClient


def _callbacks():
    calls = []
    return calls, {
        "on_open": lambda *args, **kwargs: calls.append("open"),
        "on_data": lambda *args, **kwargs: calls.append("data"),
        "on_error": lambda *args, **kwargs: calls.append("error"),
        "on_close": lambda *args, **kwargs: calls.append("close"),
    }


def test_current_socket_callbacks_are_forwarded():
    live = LiveClient()
    calls, callbacks = _callbacks()
    live.set_callbacks(**callbacks)
    smart_client = SimpleNamespace()
    live._generation = 1
    live.client = smart_client
    live._attach_callbacks(smart_client, 1)
    wsapp = object()
    smart_client.on_open(wsapp)
    smart_client.on_data(wsapp, {"token": "1", "last_traded_price": 100})
    smart_client.on_error(wsapp, "error")
    smart_client.on_close(wsapp, 1000, "closed")
    assert calls == ["open", "data", "error", "close"]


def test_stale_socket_callbacks_are_ignored():
    live = LiveClient()
    calls, callbacks = _callbacks()
    live.set_callbacks(**callbacks)
    old_client = SimpleNamespace()
    new_client = SimpleNamespace()
    live._generation = 1
    live.client = old_client
    live._attach_callbacks(old_client, 1)
    live._generation = 2
    live.client = new_client
    live._attach_callbacks(new_client, 2)
    old_wsapp = object()
    old_client.on_open(old_wsapp)
    old_client.on_data(old_wsapp, {"token": "1", "last_traded_price": 100})
    old_client.on_error(old_wsapp, "old")
    old_client.on_close(old_wsapp, 1000, "old")
    assert calls == []


def test_new_socket_callbacks_are_forwarded_after_generation_changes():
    live = LiveClient()
    calls, callbacks = _callbacks()
    live.set_callbacks(**callbacks)
    old_client = SimpleNamespace()
    new_client = SimpleNamespace()
    live._generation = 1
    live.client = old_client
    live._attach_callbacks(old_client, 1)
    live._generation = 2
    live.client = new_client
    live._attach_callbacks(new_client, 2)
    new_wsapp = object()
    new_client.on_open(new_wsapp)
    new_client.on_data(new_wsapp, {"token": "1", "last_traded_price": 100})
    assert calls == ["open", "data"]


def test_health_exposes_connection_generation_and_client():
    live = LiveClient()
    live._generation = 4
    live.client = object()
    live.state = ConnectionState.CONNECTED
    health = live.health()
    assert health["connection_generation"] == 4
    assert health["client_exists"] is True
    assert health["state"] == "CONNECTED"


def test_close_invalidates_current_connection():
    live = LiveClient()
    live._generation = 4
    live.client = SimpleNamespace(close_connection=lambda: None)
    live.close()
    assert live.state == ConnectionState.DISCONNECTED
    assert live.client is None
    assert live.smart_api is None
    assert live.feed_token is None
