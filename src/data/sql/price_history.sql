-- OHLCV

CREATE TABLE price_history (
    symbol TEXT REFERENCES underlyings(symbol),
    date DATE,
    open NUMERIC(12,4),
    high NUMERIC(12,4),
    low NUMERIC(12,4),
    close NUMERIC(12,4),
    volume BIGINT,
    PRIMARY KEY (symbol, date)
);
