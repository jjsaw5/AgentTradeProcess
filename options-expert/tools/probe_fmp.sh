#!/usr/bin/env bash
# Probe the FMP `stable` API and report which endpoints this key can reach.
# Re-run whenever the plan/tier changes — the catalog in ../DATA_LAYER.md is
# only true as of its stated verification date.
#
# Usage:  FMP_API_KEY=... ./probe_fmp.sh [outdir]
# Prints:  HTTP_CODE | name | path | response_bytes
#
# The key is read from the environment and never echoed. Do not add `set -x`.

set -uo pipefail
: "${FMP_API_KEY:?FMP_API_KEY not set}"
OUT="${1:-./fmp_probe}"
mkdir -p "$OUT"; cd "$OUT" || exit 1
rm -f results.txt

probe() {
  local name="$1" path="$2" sep="?"
  case "$path" in *\?*) sep="&";; esac
  local code
  code=$(curl -sS --max-time 20 -o "$name.json" -w '%{http_code}' \
    "https://financialmodelingprep.com/stable/${path}${sep}apikey=$FMP_API_KEY" 2>/dev/null)
  echo "$code|$name|$path|$(wc -c < "$name.json")" >> results.txt
}

TODAY=$(TZ=America/New_York date +%F)
WEEK=$(TZ=America/New_York date -d '+7 days' +%F 2>/dev/null || TZ=America/New_York date -v+7d +%F)
AGO=$(TZ=America/New_York date -d '-7 days' +%F 2>/dev/null || TZ=America/New_York date -v-7d +%F)

# price / quote
probe quote                "quote?symbol=SPY"
probe batch_quote          "batch-quote?symbols=SPY,QQQ,IWM,TSLA,NVDA"
probe quote_short          "quote-short?symbol=SPY"
probe aftermarket_quote    "aftermarket-quote?symbol=SPY"
probe aftermarket_trade    "aftermarket-trade?symbol=SPY"
probe premarket_batch      "batch-aftermarket-quote?symbols=SPY,QQQ"
for tf in 1min 5min 15min 1hour; do probe "chart_$tf" "historical-chart/$tf?symbol=SPY"; done
probe eod_full             "historical-price-eod/full?symbol=SPY"
probe eod_light            "historical-price-eod/light?symbol=SPY"
# movers / breadth
probe gainers              "biggest-gainers"
probe losers               "biggest-losers"
probe actives              "most-actives"
probe sector_perf          "sector-performance-snapshot?date=$AGO"
probe industry_perf        "industry-performance-snapshot?date=$AGO"
probe sector_pe            "sector-pe-snapshot?date=$AGO"
probe hist_sector_perf     "historical-sector-performance?sector=Technology"
# calendars / macro
probe econ_calendar        "economic-calendar?from=$TODAY&to=$WEEK"
probe earnings_calendar    "earnings-calendar?from=$TODAY&to=$WEEK"
probe earnings_symbol      "earnings?symbol=NVDA"
probe treasury             "treasury-rates?from=$AGO&to=$TODAY"
probe econ_indicators      "economic-indicators?name=GDP"
probe market_hours         "exchange-market-hours?exchange=NASDAQ"
probe dividends_cal        "dividends-calendar?from=$TODAY&to=$WEEK"
probe splits_cal           "splits-calendar?from=$TODAY&to=$WEEK"
probe ipo_cal              "ipos-calendar?from=$TODAY&to=$WEEK"
# news
probe news_stock           "news/stock?symbols=NVDA"
probe news_general         "news/general-latest"
probe press_releases       "news/press-releases?symbols=NVDA"
probe fmp_articles         "fmp-articles"
probe news_stock_latest    "news/stock-latest"
probe social_sentiment     "historical-social-sentiment?symbol=NVDA"
# analyst
probe price_target_news    "price-target-news?symbol=NVDA"
probe price_target_summary "price-target-summary?symbol=NVDA"
probe grades_latest        "grades-latest-news"
probe grades_consensus     "grades-consensus?symbol=NVDA"
probe ratings_snapshot     "ratings-snapshot?symbol=NVDA"
probe analyst_estimates    "analyst-estimates?symbol=NVDA&period=annual"
# fundamentals
probe profile              "profile?symbol=NVDA"
probe key_metrics_ttm      "key-metrics-ttm?symbol=NVDA"
probe ratios_ttm           "ratios-ttm?symbol=NVDA"
probe earnings_surprises   "earnings-surprises-bulk?year=2026"
probe float                "shares-float?symbol=NVDA"
probe sp500                "sp500-constituent"
probe stock_screener       "company-screener?marketCapMoreThan=10000000000&limit=5"
# technicals
probe rsi                  "technical-indicators/rsi?symbol=SPY&periodLength=14&timeframe=5min"
probe ema                  "technical-indicators/ema?symbol=SPY&periodLength=20&timeframe=5min"
probe sma                  "technical-indicators/sma?symbol=SPY&periodLength=50&timeframe=1day"
probe stddev               "technical-indicators/standarddeviation?symbol=SPY&periodLength=20&timeframe=1day"
probe adx                  "technical-indicators/adx?symbol=SPY&periodLength=14&timeframe=1day"
# positioning
probe insider_trades       "insider-trading/latest"
probe inst_holder          "institutional-ownership/symbol-positions-summary?symbol=NVDA&year=2026&quarter=2"
probe cot_report           "commitment-of-traders-report?symbol=ES"
probe cot_analysis         "commitment-of-traders-analysis?symbol=ES"
probe etf_holdings         "etf/holdings?symbol=SPY"
probe etf_sector_weight    "etf/sector-weightings?symbol=SPY"
# options (expected 404 — FMP serves no options data on this plan)
probe options_chain        "options-chain?symbol=SPY"
probe options_quote        "options/quote?symbol=SPY"

sort -t'|' -k1 results.txt | awk -F'|' '{printf "%-5s %-24s %-9s %s\n", $1, $2, $4"B", $3}'
echo
echo "reachable: $(awk -F'|' '$1==200' results.txt | wc -l)/$(wc -l < results.txt)"
