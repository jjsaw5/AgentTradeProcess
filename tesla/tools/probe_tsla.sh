#!/usr/bin/env bash
# Re-verify tesla/DATA_LAYER-TSLA.md. Read-only. Places no orders.
#
#   ./tesla/tools/probe_tsla.sh
#
# Requires FMP_API_KEY in the environment. UNUSUAL_WHALES_API_KEY is optional;
# if unset the UW section reports the gap instead of failing the run.
# Never prints a key. Robinhood is probed separately through the MCP connector
# (see DATA_LAYER-TSLA.md §1-§3) because it has no HTTP surface here.

set -uo pipefail

# Secrets reach this script through the environment (CLAUDE.md §6).
# A gitignored .env is a LOCAL FALLBACK ONLY: it fills variables that are not
# already set, and must never override the environment. Overriding would mask a
# rotated key set in the environment config with a stale local value — and the
# probe would report a false pass. Never echo a value.
_envfile="$(dirname "$0")/../../.env"
if [ -f "$_envfile" ]; then
  while IFS= read -r _line; do
    case "$_line" in ''|\#*) continue;; esac
    _k=${_line%%=*}
    [ "$_k" = "$_line" ] && continue
    if [ -z "$(eval "printf '%s' \"\${$_k:-}\"")" ]; then
      export "$_k=${_line#*=}"
    fi
  done < "$_envfile"
fi

T=TSLA
FMP=https://financialmodelingprep.com/stable
UW=https://api.unusualwhales.com/api

hr() { printf '\n=== %s ===\n' "$1"; }

if [ -z "${FMP_API_KEY:-}" ]; then
  echo "FMP_API_KEY unset — cannot probe the context layer." >&2; exit 1
fi

hr "session gate"
curl -sS --max-time 25 "$FMP/exchange-market-hours?exchange=NASDAQ&apikey=$FMP_API_KEY" \
  | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d[0] if d else "empty")'

hr "$T quote"
curl -sS --max-time 25 "$FMP/quote?symbol=$T&apikey=$FMP_API_KEY" \
  | python3 -c 'import json,sys
d=json.load(sys.stdin)[0]
print("price %s  chg %.2f%%  dayH %s  dayL %s" % (d["price"],d["changePercentage"],d["dayHigh"],d["dayLow"]))
print("prevClose %s  vol %s  ts %s" % (d["previousClose"],format(d["volume"],","),d["timestamp"]))'

hr "$T daily range, 10 sessions"
curl -sS --max-time 25 "$FMP/historical-price-eod/full?symbol=$T&apikey=$FMP_API_KEY" \
  | python3 -c 'import json,sys,statistics as st
d=json.load(sys.stdin)[:10];rs=[]
for r in d:
    rng=r["high"]-r["low"];rs.append(rng)
    print("%s  O%8.2f H%8.2f L%8.2f C%8.2f  range %6.2f (%.2f%%)" % (r["date"],r["open"],r["high"],r["low"],r["close"],rng,100*rng/r["close"]))
print("mean range %.2f" % st.mean(rs))'

hr "$T 5-min volume distribution"
curl -sS --max-time 25 "$FMP/historical-chart/5min?symbol=$T&apikey=$FMP_API_KEY" \
  | python3 -c 'import json,sys,statistics as st
from collections import defaultdict
d=json.load(sys.stdin);byday=defaultdict(list)
for r in d:
    day,tm=r["date"].split(" ");byday[day].append((tm,r["volume"]))
allv=[v for day in byday for _,v in byday[day]]
o30=[v for day in byday for tm,v in byday[day] if "09:30"<=tm<"10:00"]
allv.sort()
print("sessions %d  bars %d" % (len(byday),len(allv)))
print("all bars   median {:,.0f}  p25 {:,.0f}  p10 {:,.0f}".format(st.median(allv),allv[len(allv)//4],allv[len(allv)//10]))
print("9:30-10:00 mean   {:,.0f}".format(st.mean(o30)))
print("provisional floor ~185,000 / re-arm ~237,000 (see DATA_LAYER-TSLA.md 5a)")'

hr "$T next earnings"
curl -sS --max-time 25 "$FMP/earnings?symbol=$T&apikey=$FMP_API_KEY" \
  | python3 -c 'import json,sys,datetime
d=json.load(sys.stdin);today=datetime.date.today().isoformat()
fut=sorted([r for r in d if r.get("date","")>=today],key=lambda r:r["date"])
print(fut[0] if fut else "no future earnings row")'

hr "unusual whales"
if [ -z "${UNUSUAL_WHALES_API_KEY:-}" ]; then
  echo "UNUSUAL_WHALES_API_KEY unset — edge layer unavailable."
  echo "E2 (flow) and E3 (dealer mechanics) cannot run. Regime = NA_unresolved."
else
  echo "rate limits (headers — there is no /api-usage endpoint):"
  curl -sS --max-time 25 -D - -o /dev/null \
    -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" -H "UW-CLIENT-API-ID: 100001" \
    "$UW/stock/$T/gex-levels" | grep -i '^x-uw' | sed 's/^/  /'
  echo
  for p in \
    "stock/$T/gex-levels" \
    "stock/$T/max-pain" \
    "stock/$T/spot-exposures/strike?limit=500" \
    "stock/$T/volatility/stats" \
    "stock/$T/iv-rank" \
    "stock/$T/volatility/term-structure" \
    "stock/$T/net-prem-ticks" \
    "stock/$T/options-volume" \
    "option-trades/flow-alerts?ticker_symbol=$T&limit=20" \
    "screener/option-contracts?ticker_symbol=$T&limit=20" \
    "stock/$T/historical-risk-reversal-skew" \
    "market/market-tide" ; do
    st=$(curl -sS --max-time 30 -o /tmp/uw_probe.json -w '%{http_code}' \
      -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" \
      -H "UW-CLIENT-API-ID: 100001" "$UW/$p")
    rows=$(python3 -c 'import json;d=json.load(open("/tmp/uw_probe.json"));x=d.get("data",d) if isinstance(d,dict) else d;print(len(x) if isinstance(x,list) else "obj")' 2>/dev/null || echo "?")
    printf '  %-52s http=%s rows=%s\n' "${p%%\?*}" "$st" "$rows"
    if [ "$st" = "200" ] && [ "$rows" = "0" ]; then
      echo "    ^ data:[] is NOT a validated negative — re-request with known-good params (DATA_LAYER §3d)"
    fi
  done
  echo
  echo "  §3e bracket assertion (spot-exposures must straddle spot):"
  curl -sS --max-time 30 -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" \
    -H "UW-CLIENT-API-ID: 100001" "$UW/stock/$T/spot-exposures/strike?limit=500" \
    -o /tmp/uw_se.json
  python3 -c '
import json
d=json.load(open("/tmp/uw_se.json")).get("data",[])
if not d: print("    no rows — cannot assert"); raise SystemExit
ks=sorted(float(r["strike"]) for r in d); spot=float(d[0].get("price") or 0)
above=[k for k in ks if k>spot]; below=[k for k in ks if k<spot]
ok=bool(above and below)
print("    rows %d  strikes %g -> %g  spot %g" % (len(d),ks[0],ks[-1],spot))
print("    above %d  below %d  BRACKETS SPOT: %s" % (len(above),len(below),ok))
print("    " + ("ok" if ok else "!! ONE-SIDED WINDOW — paging artifact, DISCARD, do not interpret"))
print("    as of:", d[0].get("time"))'
  echo
  echo "  E5 skew — series is ASCENDING, newest row is last:"
  curl -sS --max-time 30 -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" \
    -H "UW-CLIENT-API-ID: 100001" "$UW/stock/$T/historical-risk-reversal-skew" \
    -o /tmp/uw_rr.json
  python3 -c '
import json
d=json.load(open("/tmp/uw_rr.json")).get("data",[])
last=d[-6:]
for r in last: print("    %s  %s" % (r["date"], r["risk_reversal"]))
vals=[abs(float(r["risk_reversal"])) for r in last]
if len(vals)>1 and vals[-1] > 5*max(vals[:-1]):
    print("    !! newest print is an order-of-magnitude outlier — anomaly, not a reading (DATA_LAYER-TSLA §7f)")'
fi

hr "robinhood"
cat <<'MSG'
  Probed through the MCP connector, not curl. Re-verify by hand:
    get_accounts                -> option_level on the sizing account
    get_portfolio               -> live equity + buying power
    get_option_chains  TSLA     -> expirations, sellout_time_to_expiration, min_ticks
    get_option_instruments      -> per-contract sellout_datetime, strike spacing
    get_option_quotes           -> bid/ask/mark/greeks/IV/OI/volume
  Read-only. Never place, modify, or cancel an order.
MSG
