from app.account.service import AccountService


def test_account_summary():

    account = AccountService.summary()

    assert account.capital >= 0
    assert account.balance >= 0
    assert account.equity >= 0
    assert account.used_margin >= 0
    assert account.available_margin >= 0