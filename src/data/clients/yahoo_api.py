import requests
from typing import Dict, Any, List, Optional


class YahooFinanceApi:
    """
    Simple Yahoo Finance client for tradewinds.

    Uses Yahoo Finance public query endpoints to fetch quote and option
    chain information while the Schwab API access is pending.
    """

    BASE_URL = "https://query1.finance.yahoo.com"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current quote data for a symbol.
        """
        url = f"{self.BASE_URL}/v7/finance/quote"
        params = {"symbols": symbol}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("quoteResponse", {})

    def get_option_chain(self, symbol: str, date: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch option chain data for a symbol.

        If `date` is provided, it should be a Unix timestamp for the expiration
        date to load.
        """
        url = f"https://query2.finance.yahoo.com/v7/finance/options/{symbol}"
        params = {}
        if date is not None:
            params["date"] = date

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_option_expirations(self, symbol: str) -> List[int]:
        """
        Return available option expiration timestamps for a symbol.
        """
        data = self.get_option_chain(symbol)
        result = data.get("optionChain", {}).get("result")
        if not result:
            return []

        return result[0].get("expirationDates", [])

    def get_chart(self, symbol: str, interval: str = "1d", range: str = "1mo") -> Dict[str, Any]:
        """
        Fetch historical chart data for a symbol.
        """
        url = f"{self.BASE_URL}/v8/finance/chart/{symbol}"
        params = {
            "interval": interval,
            "range": range,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
