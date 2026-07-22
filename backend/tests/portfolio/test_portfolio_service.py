from app.portfolio.service import PortfolioService


def test_portfolio_summary():

    portfolio = PortfolioService.summary()

    assert portfolio.capital >= 0
    assert portfolio.invested >= 0
    assert portfolio.available >= 0
    assert portfolio.exposure >= 0
    assert portfolio.open_positions >= 0
    assert portfolio.closed_positions >= 0