import sys
import types

from app.angel.client import AngelClient


def _create_smart_api_mock():
    smart_api_module = types.ModuleType("SmartApi")

    class MockSmartConnect:
        def __init__(self, *args, **kwargs):
            pass

    smart_api_module.SmartConnect = MockSmartConnect

    return smart_api_module


class AngelClientTests:

    def test_get_client_initializes_when_none_exists(
        self,
        monkeypatch,
    ):

        smart_api_module = _create_smart_api_mock()

        monkeypatch.setitem(
            sys.modules,
            "SmartApi",
            smart_api_module,
        )

        AngelClient._client = None

        client = AngelClient.get_client()

        assert client is not None

    def test_get_client_returns_existing_client(
        self,
        monkeypatch,
    ):

        smart_api_module = _create_smart_api_mock()

        monkeypatch.setitem(
            sys.modules,
            "SmartApi",
            smart_api_module,
        )

        existing_client = object()

        AngelClient._client = existing_client

        client = AngelClient.get_client()

        assert client is existing_client