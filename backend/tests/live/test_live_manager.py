from types import SimpleNamespace
from unittest.mock import Mock

from app.live.manager import LiveManager


def _fake_live_client(generation: int):
    broker_client = SimpleNamespace(
        subscribe=Mock(),
        unsubscribe=Mock(),
    )
    live_client = SimpleNamespace(
        client=broker_client,
        health=Mock(
            return_value={
                "connection_generation": generation,
                "state": "CONNECTED",
            }
        ),
    )
    return live_client, broker_client


def test_subscription_state_is_rebuilt_for_new_websocket_generation():
    manager = LiveManager()
    live_client, broker_client = _fake_live_client(generation=2)
    manager.client = live_client

    manager._subscribed_generation = 1
    manager.subscribed_tokens = {"OLD_TOKEN"}

    manager.subscribe("NSE", "NEW_TOKEN")

    broker_client.subscribe.assert_called_once()
    assert "OLD_TOKEN" not in manager.subscribed_tokens
    assert "NEW_TOKEN" in manager.subscribed_tokens
    assert manager._subscribed_generation == 2


def test_same_token_is_not_subscribed_twice_on_same_generation():
    manager = LiveManager()
    live_client, broker_client = _fake_live_client(generation=2)
    manager.client = live_client

    manager._subscribed_generation = 2
    manager.subscribed_tokens = {"123"}

    manager.subscribe("NSE", "123")

    broker_client.subscribe.assert_not_called()
