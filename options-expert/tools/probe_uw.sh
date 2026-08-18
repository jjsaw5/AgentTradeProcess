#!/usr/bin/env bash
# Probe the Unusual Whales API and report which endpoints this key can reach.
# Endpoint list is the whitelist from https://unusualwhales.com/skill.md —
# that document is authoritative and includes a blacklist of commonly
# hallucinated paths. Do not add a path here that is not on it (except the
# deliberately-flagged off-list probes at the bottom).
#
# Usage:  UNUSUAL_WHALES_API_KEY=... ./probe_uw.sh [outdir]
# Prints: HTTP_CODE | name | path | response_bytes
#
# The key is read from the environment and never echoed. Do not add `set -x`.
#
# NOTE: Python's urllib has historically failed on UW's cert chain from this
# stack — fetch via curl, as here.

set -uo pipefail
: "${UNUSUAL_WHALES_API_KEY:?UNUSUAL_WHALES_API_KEY not set}"
UW_BASE="${UNUSUAL_WHALES_BASE_URL:-https://api.unusualwhales.com}"
OUT="${1:-./uw_probe}"
mkdir -p "$OUT"; cd "$OUT" || exit 1
rm -f results.txt

uw() {
  local name="$1" path="$2" code
  code=$(curl -sS --max-time 25 -o "$name.json" -w '%{http_code}' \
    -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" \
    -H "UW-CLIENT-API-ID: 100001" \
    -H "Accept: application/json" \
    "${UW_BASE}${path}" 2>/dev/null)
  echo "$code|$name|$path|$(wc -c < "$name.json")" >> results.txt
}

T="${TICKER:-SPY}"; F="${FUNDA_TICKER:-NVDA}"

# Core flow
uw option_trades    "/api/option-trades?limit=5&ticker_symbol=$T"
uw flow_alerts      "/api/option-trades/flow-alerts?limit=5"
uw screener         "/api/screener/option-contracts?limit=5"
uw flow_recent      "/api/stock/$T/flow-recent"
uw darkpool_ticker  "/api/darkpool/$T"
uw darkpool_recent  "/api/darkpool/recent?limit=5"
uw market_tide      "/api/market/market-tide"
uw market_tide_5m   "/api/market/market-tide?interval_5m=true"
uw net_prem_ticks   "/api/stock/$T/net-prem-ticks"
# Options, greeks, IV
uw option_contracts "/api/stock/$T/option-contracts"
uw greeks           "/api/stock/$T/greeks"
uw gex_static       "/api/stock/$T/greek-exposure/strike"
uw gex_spot         "/api/stock/$T/spot-exposures/strike"
uw interp_iv        "/api/stock/$T/interpolated-iv"
uw options_volume   "/api/stock/$T/options-volume"
# Other
uw insider          "/api/insider/transactions?limit=5"
uw congress         "/api/congress/recent-trades?limit=5"
uw news             "/api/news/headlines?limit=5"
# Financials
uw financials       "/api/stock/$F/financials"
uw income           "/api/stock/$F/income-statements"
uw balance          "/api/stock/$F/balance-sheets"
uw cashflow         "/api/stock/$F/cash-flows"
uw earnings         "/api/stock/$F/earnings"
# Technicals — interval MUST be daily|weekly|monthly. An unrecognised interval
# returns HTTP 200 with data:[] rather than an error. Probe one good and one
# bad so a regression in that behaviour is visible.
uw tech_rsi_daily   "/api/stock/$T/technical-indicator/rsi?interval=daily&time_period=14"
uw tech_rsi_bad     "/api/stock/$T/technical-indicator/rsi?interval=5m&time_period=14"
# Off-whitelist, verified working anyway — see DATA_LAYER.md 3a
uw iv_rank_offlist  "/api/stock/$T/iv-rank"

sort -t'|' -k1 results.txt | awk -F'|' '{printf "%-5s %-20s %-9s %s\n", $1, $2, $4"B", $3}'
echo
echo "reachable: $(awk -F'|' '$1==200' results.txt | wc -l)/$(wc -l < results.txt)"
echo "NOTE: HTTP 200 with an empty data[] is NOT success — check row counts too."
