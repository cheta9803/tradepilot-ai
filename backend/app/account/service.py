from app.account.models import Account
from app.core.config import settings
from app.portfolio.service import PortfolioService


class AccountService:

    @classmethod
    def summary(cls) -> Account:

        portfolio = PortfolioService.summary()

        balance = (
            settings.default_capital
            + portfolio.realized_pnl
        )

        equity = (
            balance
            + portfolio.unrealized_pnl
        )

        used_margin = portfolio.invested

        available_margin = (
            equity
            - used_margin
        )

        return Account(
            capital=settings.default_capital,
            balance=round(balance, 2),
            equity=round(equity, 2),
            used_margin=round(used_margin, 2),
            available_margin=round(
                available_margin,
                2,
            ),
            realized_pnl=portfolio.realized_pnl,
            unrealized_pnl=portfolio.unrealized_pnl,
            total_pnl=portfolio.total_pnl,
        )