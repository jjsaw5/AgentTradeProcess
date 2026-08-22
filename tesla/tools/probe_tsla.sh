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
  echo "UNUSUAL_WHALES_API_KEY unset — edge layer UNAVAILABLE."
  echo "E2 (flow) and E3 (dealer mechanics) cannot run. Regime = NA_unresolved."
else
  for p in "stock/$T/gex-levels" "stock/$T/volatility/stats" "stock/$T/net-prem-ticks"; do
    st=$(curl -sS --max-time 25 -o /tmp/uw_probe.json -w '%{http_code}' \
      -H "Authorization: Bearer $UNUSUAL_WHALES_API_KEY" \
      -H "UW-CLIENT-API-ID: 100001" "$UW/$p")
    rows=$(python3 -c 'import json;d=json.load(open("/tmp/uw_probe.json"));x=d.get("data",d);print(len(x) if isinstance(x,list) else "obj")' 2>/dev/null || echo "?")
    printf '  %-34s http=%s rows=%s\n' "$p" "$st" "$rows"
    [ "$st" = "200" ] && [ "$rows" = "0" ] && echo "    ^ data:[] is NOT a negative result — re-request with known-good params"
  done
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
