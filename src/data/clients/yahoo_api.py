import re
import time
import requests
from requests.exceptions import HTTPError, RequestException
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
        self._crumb_cache: Dict[str, str] = {}

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

    def _get_html(self, url: str, params: Optional[dict] = None) -> str:
        html_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, headers=html_headers, timeout=10)
            except RequestException:
                if attempt == self.max_retries - 1:
                    raise
                wait = self.backoff_factor * 2**attempt
                time.sleep(wait)
                continue

            if response.status_code in {429, 500, 502, 503, 504}:
                if attempt == self.max_retries - 1:
                    response.raise_for_status()
                wait = self.backoff_factor * 2**attempt
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.text

        raise RuntimeError(f"Failed to GET HTML {url} after {self.max_retries} retries")

    def _extract_crumb(self, html: str) -> Optional[str]:
        match = re.search(r'"crumb"\s*:\s*"([^"]+)"', html)
        if not match:
            return None

        raw_crumb = match.group(1)
        return raw_crumb.encode("utf-8").decode("unicode_escape")

    def _get_crumb(self, symbol: str) -> Optional[str]:
        html = self._get_html(f"https://finance.yahoo.com/quote/{symbol}")
        return self._extract_crumb(html)

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current quote data for a symbol.
        """
        url = f"{self.BASE_URL}/v7/finance/quote"
        params = {"symbols": symbol}

        crumb = self._crumb_cache.get(symbol)
        if crumb:
            params["crumb"] = crumb

        try:
            data = self._get_json(url, params=params)
            return data.get("quoteResponse", {})
        except HTTPError as exc:
            response = getattr(exc, "response", None)
            if response is not None and response.status_code == 401:
                crumb = self._get_crumb(symbol)
                if crumb:
                    self._crumb_cache[symbol] = crumb
                    params["crumb"] = crumb
                    data = self._get_json(url, params=params)
                    return data.get("quoteResponse", {})
            raise

    def get_option_chain(self, symbol: str, date: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch option chain data for a symbol.

        If `date` is provided, it should be a Unix timestamp for the expiration
        date to load.
        """
        url = f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
        params = {}
        if date is not None:
            params["date"] = date

        crumb = self._crumb_cache.get(symbol)
        if crumb:
            params["crumb"] = crumb

        try:
            return self._get_json(url, params=params)
        except HTTPError as exc:
            response = getattr(exc, "response", None)
            if response is not None and response.status_code == 401:
                crumb = self._get_crumb(symbol)
                if crumb:
                    self._crumb_cache[symbol] = crumb
                    params["crumb"] = crumb
                    return self._get_json(url, params=params)
            raise

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
