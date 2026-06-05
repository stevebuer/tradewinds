#!/bin/bash

# Use curl and jq to test connectivity to Yahoo finance API
# A browser-style User-Agent helps avoid automatic rate-limit rejections.

TICKER=HRL

curl -s -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64)' \
  "https://query1.finance.yahoo.com/v8/finance/chart/${TICKER}?interval=1d&range=1d" \
  | jq .
