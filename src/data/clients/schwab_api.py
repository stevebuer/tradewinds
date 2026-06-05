import requests
import time
from typing import Dict, Any


class SchwabApi:
    """
    Schwab API client for tradewinds.

    The exact Schwab OAuth and option chain endpoints should be updated to
    match the current Schwab API documentation.
    """

    def __init__(
        self,
        client_id: str,
        refresh_token: str,
        base_url: str = "https://api.schwab.com",
    ):
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = 0
        self.base_url = base_url.rstrip("/")

    def _refresh_access_token(self) -> None:
        """
        Refresh the OAuth access token using the Schwab token endpoint.
        """
        url = f"{self.base_url}/openapi/oauth2/token"

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()

        data = response.json()
        self.access_token = data["access_token"]
        self.token_expiry = time.time() + data.get("expires_in", 1800)

    def _ensure_token(self) -> None:
        """
        Refresh token if expired or missing.
        """
        if not self.access_token or time.time() >= self.token_expiry:
            self._refresh_access_token()

    def get_option_chain(
        self,
        symbol: str,
        contract_type: str = "ALL",
        strike_count: int = 20,
        include_quotes: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch option chain data for a given symbol from Schwab.
        """
        self._ensure_token()

        url = f"{self.base_url}/openapi/marketdata/chains"

        params = {
            "symbol": symbol,
            "contractType": contract_type,
            "strikeCount": strike_count,
            "includeQuotes": include_quotes,
            "apikey": self.client_id,
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

