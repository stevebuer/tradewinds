import time
import requests
from requests.exceptions import RequestException
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
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "Accept": "application/json, text/plain, */*",
        })
        self.max_retries = 5
        self.backoff_factor = 1

    def _get_json(self, url: str, params: Optional[dict] = None) -> Dict[str, Any]:
        retry_statuses = {429, 500, 502, 503, 504}

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
            except RequestException:
                if attempt == self.max_retries - 1:
                    raise
                wait = self.backoff_factor * 2**attempt
                time.sleep(wait)
                continue

            if response.status_code in retry_statuses:
                if attempt == self.max_retries - 1:
                    response.raise_for_status()
                wait = self.backoff_factor * 2**attempt
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError(f"Failed to GET {url} after {self.max_retries} retries")

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current quote data for a symbol.
        """
        url = f"{self.BASE_URL}/v7/finance/quote"
        params = {"symbols": symbol}

        data = self._get_json(url, params=params)
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

        return self._get_json(url, params=params)

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

        return self._get_json(url, params=params)
