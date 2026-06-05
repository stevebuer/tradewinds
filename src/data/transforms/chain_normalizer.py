from typing import Dict, Any, List
from datetime import datetime


class ChainNormalizer:
    """
    Normalizes TD Ameritrade option chain JSON into flat rows
    suitable for PostgreSQL insertion.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def normalize_chain(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert TD Ameritrade's nested option chain JSON into
        a list of flat dictionaries.
        """
        rows = []

        underlying = raw.get("symbol")
        quote_time = self._convert_timestamp(raw.get("quoteTime"))

        # TD splits calls and puts into nested maps:
        #   callExpDateMap -> { "2024-06-21:28": { "100.0": [ {...}, ... ] } }
        #   putExpDateMap  -> same structure
        #
        # We normalize both sides.
        rows.extend(self._extract_side(raw.get("callExpDateMap", {}),
                                       underlying, quote_time, "call"))
        rows.extend(self._extract_side(raw.get("putExpDateMap", {}),
                                       underlying, quote_time, "put"))

        return rows

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------
    def _extract_side(
        self,
        side_map: Dict[str, Any],
        underlying: str,
        quote_time: datetime,
        option_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts either calls or puts from TD's nested structure.
        """
        rows = []

        for exp_key, strikes in side_map.items():
            # exp_key looks like "2024-06-21:28"
            expiration = exp_key.split(":")[0]

            for strike_str, contracts in strikes.items():
                strike = float(strike_str)

                for contract in contracts:
                    rows.append({
                        "underlying": underlying,
                        "quote_time": quote_time,
                        "expiration": expiration,
                        "strike": strike,
                        "option_type": option_type,
                        "bid": contract.get("bid"),
                        "ask": contract.get("ask"),
                        "last": contract.get("last"),
                        "delta": contract.get("delta"),
                        "gamma": contract.get("gamma"),
                        "theta": contract.get("theta"),
                        "vega": contract.get("vega"),
                        "implied_vol": contract.get("volatility"),
                        "open_interest": contract.get("openInterest"),
                        "volume": contract.get("totalVolume")
                    })

        return rows

    def _convert_timestamp(self, ts: Any) -> datetime:
        """
        Convert TD Ameritrade millisecond timestamp to datetime.
        """
        if ts is None:
            return None
        return datetime.fromtimestamp(ts / 1000)

