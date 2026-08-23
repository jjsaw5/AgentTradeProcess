#!/usr/bin/env bash
# RTH probe — measures what a closed-market probe structurally cannot.
#
#   ./tesla/tools/probe_rth.sh            # human-readable
#   ./tesla/tools/probe_rth.sh --md       # markdown block for tesla/log/rth/
#
# Read-only. Places no orders. Never prints a key.
#
# WHY THIS EXISTS: tesla/DATA_LAYER-TSLA.md was verified on a Saturday. Every
# liquidity number in it is a closing snapshot, and closing spreads are the
# widest of the day. Three things in the spec are therefore uncalibrated in a
# way only a live session can fix — see tesla/log/rth/PREREGISTRATION.md.
#
# This script covers the FMP + UW half. The option-chain half (live bid/ask,
# the 5% spread gate, contract theta) needs the Robinhood MCP connector and so
# runs from the scheduled Claude session, not from bash.

set -uo pipefail
if [ -f "$(dirname "$0")/../../.env" ]; then set -a; . "$(dirname "$0")/../../.env"; set +a; fi

T=TSLA
FMP=https://financialmodelingprep.com/stable
UW=https://api.unusualwhales.com/api
NOW=$(date -u +%s)
MD=0; [ "${1:-}" = "--md" ] && MD=1

hr() { if [ "$MD" = 1 ]; then printf '\n### %s\n\n```\n' "$1"; else printf '\n=== %s ===\n' "$1"; fi; }
endblk() { [ "$MD" = 1 ] && printf '```\n'; return 0; }

uw() { curl -sS --max-time 30 -H "Authorization: Bearer ${UNUSUAL_WHALES_API_KEY:-}" \
       -H "UW-CLIENT-API-ID: 100001" "$UW/$1"; }

echo "TSLA RTH PROBE — $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S ET') / $(date -u '+%H:%M:%S UTC')"

hr "session gate — is this actually RTH?"
curl -sS --max-time 25 "$FMP/exchange-market-hours?exchange=NASDAQ&apikey=$FMP_API_KEY" \
 | python3 -c '
import json,sys
d=json.load(sys.stdin)[0]
print("isMarketOpen:",d["isMarketOpen"],"  hours:",d["openingHour"],"-",d["closingHour"])
if not d["isMarketOpen"]:
    print("!! MARKET CLOSED — every reading below is a stale snapshot.")
    print("   An RTH probe run outside RTH answers none of the questions it exists for.")'
endblk

hr "feed freshness — lag in seconds behind now"
python3 - "$NOW" <<'PY'
import json,subprocess,sys,os,datetime
now=int(sys.argv[1]); fmp=os.environ.get("FMP_API_KEY",""); key=os.environ.get("UNUSUAL_WHALES_API_KEY","")
def curl(u,hdrs=()):
    a=["curl","-sS","--max-time","30"]
    for h in hdrs: a+=["-H",h]
    a.append(u)
    try: return json.loads(subprocess.run(a,capture_output=True,text=True).stdout)
    except Exception: return None
UWH=(f"Authorization: Bearer {key}","UW-CLIENT-API-ID: 100001")
def iso(s):
    if not s: return None
    s=s.replace("Z","+00:00")
    try: return datetime.datetime.fromisoformat(s).timestamp()
    except Exception: return None
rows=[]
d=curl(f"https://financialmodelingprep.com/stable/historical-chart/5min?symbol=TSLA&apikey={fmp}")
if d:
    t=datetime.datetime.strptime(d[0]["date"],"%Y-%m-%d %H:%M:%S")
    t=t.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-4)))  # ET in DST
    rows.append(("fmp 5-min bar", d[0]["date"]+" ET", now-int(t.timestamp())))
d=curl(f"https://financialmodelingprep.com/stable/aftermarket-quote?symbol=TSLA&apikey={fmp}")
if d and isinstance(d,list) and d:
    ts=d[0].get("timestamp"); ts=ts/1000 if ts and ts>1e11 else ts
    rows.append(("fmp aftermarket-quote", str(d[0].get("timestamp")), now-int(ts) if ts else "?"))
d=curl("https://api.unusualwhales.com/api/stock/TSLA/spot-exposures/strike?limit=500",UWH)
if d and d.get("data"):
    t=iso(d["data"][0].get("time")); rows.append(("uw spot-exposures", d["data"][0].get("time"), now-int(t) if t else "?"))
d=curl("https://api.unusualwhales.com/api/stock/TSLA/net-prem-ticks",UWH)
if d and d.get("data"):
    t=iso(d["data"][-1].get("tape_time")); rows.append(("uw net-prem-ticks", d["data"][-1].get("tape_time"), now-int(t) if t else "?"))
d=curl("https://api.unusualwhales.com/api/market/market-tide",UWH)
if d and d.get("data"):
    t=iso(d["data"][-1].get("timestamp")); rows.append(("uw market-tide", d["data"][-1].get("timestamp"), now-int(t) if t else "?"))
print("%-24s %-34s %s" % ("feed","payload timestamp","lag"))
for n,ts,lag in rows:
    flag=""
    if isinstance(lag,int):
        if lag<0: flag="  (clock skew or a bar in progress)"
        elif lag>900: flag="  <-- STALE"
    print("%-24s %-34s %ss%s" % (n,ts,lag,flag))
print()
print("gex-levels carries NO timestamp — its freshness cannot be read off the payload.")
PY
endblk

hr "live regime"
uw "stock/$T/gex-levels" | python3 -c '
import json,sys
d=json.load(sys.stdin).get("data",{})
print("call_wall %s  put_wall %s  gamma_magnet %s  gamma_flip %s" % (
  d.get("call_wall"),d.get("put_wall"),d.get("gamma_magnet"),d.get("gamma_flip")))'
curl -sS --max-time 25 "$FMP/quote-short?symbol=$T&apikey=$FMP_API_KEY" \
 | python3 -c '
import json,sys;d=json.load(sys.stdin)[0];print("spot %s  vol %s" % (d["price"],format(d["volume"],",")))'
echo "-> spot above gamma_flip = positive gamma (GLUE); below = negative (GASOLINE)"
uw "stock/$T/max-pain" | python3 -c '
import json,sys
for r in json.load(sys.stdin).get("data",[])[:3]:
    print("max-pain %s: %s" % (r["expiry"],r["max_pain"]))
print("-> magnet and max-pain disagreeing is REPORTED, never resolved by picking one")'
endblk

hr "volume floor — live check against the provisional ~185,000"
curl -sS --max-time 25 "$FMP/historical-chart/5min?symbol=$T&apikey=$FMP_API_KEY" \
 | python3 -c '
import json,sys
d=json.load(sys.stdin)
# newest first; [0] may be the bar in progress, so judge on [1] and [2]
bars=d[1:3]
print("last two COMPLETED 5-min bars:")
for b in bars: print("  %s  %s" % (b["date"],format(b["volume"],",")))
if len(bars)==2:
    armed = all(b["volume"] < 185000 for b in bars)
    print("  floor: %s" % ("ARMED — no new entries (both under 185,000)" if armed else "clear"))
print("  (bar in progress, excluded: %s %s)" % (d[0]["date"],format(d[0]["volume"],",")))'
endblk

hr "E5 skew — is the 2026-08-21 outlier confirmed or cleared?"
uw "stock/$T/historical-risk-reversal-skew" | python3 -c '
import json,sys
d=json.load(sys.stdin).get("data",[])[-6:]
for r in d: print("  %s  %s" % (r["date"],r["risk_reversal"]))
v=[abs(float(r["risk_reversal"])) for r in d]
if len(v)>1 and v[-1] > 5*max(v[:-1]):
    print("  !! newest is an order-of-magnitude outlier — anomaly, not a reading")
elif len(v)>2 and v[-2] > 5*max(v[:-2]+v[-1:]):
    print("  -> the PRIOR print was the outlier and the series has returned to band:")
    print("     the 2026-08-21 value was an artifact. Record it and clear the caveat.")
else:
    print("  -> series in band")'
endblk

hr "flow"
uw "stock/$T/options-volume" | python3 -c '
import json,sys
d=json.load(sys.stdin).get("data",[])
if not d: print("data:[] — NOT a validated negative; re-request"); raise SystemExit
r=d[0]
cv,pv=r["call_volume"],r["put_volume"]
avg=float(r["avg_30_day_call_volume"])
print("call vol %s  put vol %s   call rel-vol %.2fx 30d avg" % (format(cv,","),format(pv,","),cv/avg))
print("net call prem %s   net put prem %s" % (r["net_call_premium"],r["net_put_premium"]))'
uw "market/market-tide" | python3 -c '
import json,sys
d=json.load(sys.stdin).get("data",[])
if d:
    r=d[-1]; c=float(r["net_call_premium"]); p=float(r["net_put_premium"])
    print("tide %s  net call $%.1fM  net put $%.1fM" % (r["timestamp"],c/1e6,p/1e6))
    if c<0 and p<0: print("  -> BOTH NEGATIVE = premium liquidation / pin-decay, not direction")'
endblk

hr "what bash cannot answer — run these from the Claude session"
cat <<'MSG'
The option-chain half needs the Robinhood MCP connector:
  get_option_chains TSLA         -> today's 0DTE expiry (Mon/Wed/Fri only)
  get_option_instruments         -> strikes bracketing spot, $2.50 steps
  get_option_quotes              -> LIVE bid/ask, mark, greeks, volume
Record per near-money strike: spread %, delta, theta as %/day, same-day volume.
That is the measurement the 5% spread gate has never been tested against.
MSG
endblk
echo
echo "Append this run to tesla/log/rth/YYYY-MM-DD.md. Do not overwrite prior samples."
