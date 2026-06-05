from universe_loader import UniverseLoader


if __name__ == "__main__":
    loader = UniverseLoader(
        dbname="tradewinds",
        user="tradewinds_user",
        password="YOUR_DB_PASSWORD",
        host="localhost"
    )

    rows = [
        {
            "symbol": "KO",
            "name": "Coca-Cola Co",
            "sector": "Consumer Staples",
            "industry": "Beverages—Non-Alcoholic",
            "is_active": True,
            "is_wheel_candidate": True,
            "dividend_yield": 0.029,
            "market_cap": 260_000_000_000,
            "beta": 0.6,
        }
    ]

    loader.upsert_universe(rows)
    loader.close()

