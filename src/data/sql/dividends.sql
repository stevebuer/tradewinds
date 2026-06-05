-- Create tables for dividend data

CREATE TABLE dividend_kings (
    ticker TEXT PRIMARY KEY,
    quarterly_dividend NUMERIC,
    years_of_payment INT,
    years_of_growth INT
);

CREATE TABLE dividend_aristocrats (
    ticker TEXT PRIMARY KEY,
    quarterly_dividend NUMERIC,
    years_of_payment INT,
    years_of_growth INT
);

CREATE TABLE dividend_compounders (
    ticker TEXT PRIMARY KEY,
    quarterly_dividend NUMERIC,
    years_of_payment INT,
    years_of_growth INT
);
