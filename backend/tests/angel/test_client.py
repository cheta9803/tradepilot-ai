import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

smart_api_module = types.ModuleType("SmartApi")


class FakeSmartConnect:
    pass


smart_api_module.SmartConnect = FakeSmartConnect
sys.modules["SmartApi"] = smart_api_module

pyotp_module = types.ModuleType("pyotp")


class FakeTOTP:
    def __init__(self, secret):
        self.secret = secret

    def now(self):
        return "123456"


pyotp_module.TOTP = FakeTOTP
sys.modules["pyotp"] = pyotp_module

exceptions_module = types.ModuleType("app.angel.exceptions")


class AngelAPIException(Exception):
    pass


exceptions_module.AngelAPIException = AngelAPIException
sys.modules["app.angel.exceptions"] = exceptions_module

config_module = types.ModuleType("app.core.config")


class DummySettings:
    angel_api_key = "test-key"
    angel_client_id = "test-client"
    angel_pin = "1234"
    angel_totp_secret = "test-secret"


config_module.settings = DummySettings()
sys.modules["app.core.config"] = config_module

sys.modules.pop("app.angel.client", None)

from app.angel.client import AngelClient


class AngelClientTests(unittest.TestCase):
    def setUp(self):
        AngelClient.reset()

    def test_get_client_initializes_when_none_exists(self):
        with patch.object(AngelClient, "login", return_value="client") as login_mock:
            self.assertEqual(AngelClient.get_client(), "client")
            login_mock.assert_called_once_with()

    def test_get_client_returns_existing_client(self):
        existing = object()
        AngelClient._client = existing
        self.assertIs(AngelClient.get_client(), existing)


if __name__ == "__main__":
    unittest.main()
