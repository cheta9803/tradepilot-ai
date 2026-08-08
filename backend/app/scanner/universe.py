class Nifty50Universe:

    SYMBOLS = frozenset(
        {
            "ADANIENT",
            "ADANIPORTS",
            "APOLLOHOSP",
            "ASIANPAINT",
            "AXISBANK",
            "BAJAJ-AUTO",
            "BAJFINANCE",
            "BAJAJFINSV",
            "BEL",
            "BHARTIARTL",
            "CIPLA",
            "COALINDIA",
            "DRREDDY",
            "EICHERMOT",
            "ETERNAL",
            "GRASIM",
            "HCLTECH",
            "HDFCBANK",
            "HDFCLIFE",
            "HEROMOTOCO",
            "HINDALCO",
            "HINDUNILVR",
            "ICICIBANK",
            "INDUSINDBK",
            "INFY",
            "ITC",
            "JIOFIN",
            "JSWSTEEL",
            "KOTAKBANK",
            "LT",
            "M&M",
            "MARUTI",
            "MAXHEALTH",
            "NESTLEIND",
            "NTPC",
            "ONGC",
            "POWERGRID",
            "RELIANCE",
            "SBILIFE",
            "SBIN",
            "SHRIRAMFIN",
            "SUNPHARMA",
            "TATACONSUM",
            "TATAMOTORS",
            "TATASTEEL",
            "TCS",
            "TECHM",
            "TITAN",
            "TRENT",
            "ULTRACEMCO",
        }
    )

    @classmethod
    def contains(
        cls,
        symbol: str,
    ) -> bool:

        return symbol.upper() in cls.SYMBOLS