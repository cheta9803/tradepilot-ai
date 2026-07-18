from app.portfolio.service import PortfolioService


class CapitalManager:

    @classmethod
    def portfolio(cls):

        return PortfolioService.summary()

    @classmethod
    def has_capital(
        cls,
        invested: float,
    ) -> bool:

        portfolio = cls.portfolio()

        return portfolio.available >= invested

    @classmethod
    def available(cls) -> float:

        return cls.portfolio().available

    @classmethod
    def invested(cls) -> float:

        return cls.portfolio().invested

    @classmethod
    def realized_pnl(cls) -> float:

        return cls.portfolio().realized_pnl