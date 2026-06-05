#!/bin/bash
while read symbol; do
    python3 /path/to/tradewinds/scripts/ingest_chain.py "$symbol"
done < /path/to/tradewinds/symbols.txt
