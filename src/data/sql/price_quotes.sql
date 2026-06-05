-- stock price live quotes

CREATE TABLE price_quotes (
    symbol TEXT REFERENCES underlyings(symbol),
    price NUMERIC(12,4),
    bid NUMERIC(12,4),
    ask NUMERIC(12,4),
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);
