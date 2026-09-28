#!/usr/bin/env bash
# Re-verify the odte-desk §8 HTTP sources. Prints HTTP_CODE | name | bytes.
# Keys are read from the environment and never echoed. Do not add `set -x`.
# Usage: FMP_API_KEY=... ./probe_desk.sh [outdir]
set -uo pipefail
OUT="${1:-./desk_probe}"; mkdir -p "$OUT"; cd "$OUT" || exit 1
f() { local name="$1" url="$2" code; code=$(curl -sSL --max-time 25 -o "$name.json" -w '%{http_code}' "$url" 2>/dev/null); echo "$code|$name|$(wc -c < "$name.json")"; }
B="https://financialmodelingprep.com/stable"
# VIX complex: FMP gates everything but ^VIX (402); Cboe delayed JSON serves all four (307 -> cdn-api, follow redirects).
for s in VIX VIX1D VIX9D VIX3M; do f "fmp_$s" "$B/quote?symbol=%5E$s&apikey=${FMP_API_KEY:?}"; f "cboe_$s" "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_$s.json"; done
# Index futures on FMP: ESUSD works on this plan, NQUSD is 402. Bars carry the overnight session.
for s in ESUSD NQUSD YMUSD RTYUSD; do f "fmp_$s" "$B/quote?symbol=$s&apikey=$FMP_API_KEY"; done
f fmp_es_5min "$B/historical-chart/5min?symbol=ESUSD&apikey=$FMP_API_KEY"
# Treasury auctions, public, no key.
f td_auctioned "https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&pagesize=10"
