from price_history_loader import PriceHistoryLoader
from yahoo_client import YahooClient  # your existing client

loader = PriceHistoryLoader(
    dbname="tradewinds",
    user="tradewinds_user",
    password="YOUR_DB_PASSWORD"
)

client = YahooClient()

bars = client.get_daily_bars("KO", period="5y")

rows = []
for bar in bars:
    rows.append({
        "symbol": "KO",
        "date": bar["date"],
        "open": bar["open"],
        "high": bar["high"],
        "low": bar["low"],
        "close": bar["close"],
        "volume": bar["volume"]
    })

loader.upsert_price_history(rows)
loader.close()

