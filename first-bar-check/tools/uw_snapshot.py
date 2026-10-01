#!/usr/bin/env python3
"""First-bar check: one-shot Unusual Whales snapshot for SPY and QQQ.

Prints a compact JSON summary to stdout. Never prints the API key.

Key: UNUSUAL_WHALES_API_KEY from the environment, or the repo's gitignored
.env. Every request uses the hardened curl rule from
daily-market-brief/SKILL.md (fail-with-body, timeout, retries). The key is
passed to curl through a mode-600 header file, never on the command line.

Honesty rules (CLAUDE.md §3, DATA_LAYER §3d/§3e):
  - a failed request, an empty `data: []`, or a stale timestamp is reported
    as UNVERIFIED with the reason; it is never turned into zero or "none";
  - spot-exposures must bracket spot (strikes above AND below) or it is
    discarded as a paging artifact.

Usage:  uw_snapshot.py [--date YYYY-MM-DD] [--since HH:MM]   (ET)
"""
import json, os, subprocess, sys, tempfile, datetime as dt
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BASE = "https://api.unusualwhales.com/api"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TICKERS = ("SPY", "QQQ")


def key():
    k = os.environ.get("UNUSUAL_WHALES_API_KEY", "")
    if len(k) < 20:
        envf = os.path.join(REPO, ".env")
        if os.path.exists(envf):
            for line in open(envf):
                if line.startswith("UNUSUAL_WHALES_API_KEY="):
                    k = line.strip().split("=", 1)[1]
    if len(k) < 20:
        sys.exit(json.dumps({"error": "UNUSUAL_WHALES_API_KEY not set"}))
    return k


def fetch(path, hdr):
    """Return (data, status). status is 'ok' or an UNVERIFIED reason."""
    with tempfile.NamedTemporaryFile(delete=False) as out:
        outf = out.name
    try:
        r = subprocess.run(
            ["curl", "-sS", "--fail-with-body", "-m", "20", "--retry", "2",
             "--retry-delay", "1", "--retry-all-errors", "-H", f"@{hdr}",
             "-H", "Accept: application/json", f"{BASE}/{path}", "-o", outf],
            capture_output=True, text=True)
        if r.returncode != 0:
            return None, f"UNVERIFIED — request failed (curl {r.returncode})"
        try:
            d = json.load(open(outf))
        except Exception:
            return None, "UNVERIFIED — response was not JSON"
        data = d.get("data", d) if isinstance(d, dict) else d
        if data in ([], {}, None):
            return None, "UNVERIFIED — empty response (a 200 is not a success)"
        return data, "ok"
    finally:
        os.unlink(outf)


def et_time(s):
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)
        return t.astimezone(ET)
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    today = dt.datetime.now(ET).date()
    since = dt.time(9, 30)
    if "--date" in args:
        today = dt.date.fromisoformat(args[args.index("--date") + 1])
    if "--since" in args:
        hh, mm = args[args.index("--since") + 1].split(":")
        since = dt.time(int(hh), int(mm))
    k = key()
    fd, hdr = tempfile.mkstemp()
    os.write(fd, f"Authorization: Bearer {k}\n".encode())
    os.close(fd)
    os.chmod(hdr, 0o600)
    out = {"date": str(today), "generated_et": dt.datetime.now(ET).strftime("%H:%M:%S")}
    try:
        for t in TICKERS:
            o = {}
            # vendor levels
            d, st = fetch(f"stock/{t}/gex-levels", hdr)
            if st == "ok":
                when = et_time(d.get("time")) if isinstance(d, dict) else None
                fresh = bool(when and when.date() == today)
                o["levels"] = {k2: d.get(k2) for k2 in
                               ("call_wall", "put_wall", "gamma_magnet", "gamma_flip", "nearby_flips")}
                o["levels"]["as_of_et"] = when.strftime("%m-%d %H:%M") if when else None
                o["levels"]["status"] = "ok" if fresh else "UNVERIFIED — stale timestamp (not today)"
            else:
                o["levels"] = {"status": st}
            # live spot exposures, bracket check
            d, st = fetch(f"stock/{t}/spot-exposures/strike?limit=500", hdr)
            if st == "ok" and isinstance(d, list):
                price = None
                rows = []
                for r in d:
                    try:
                        strike = float(r.get("strike"))
                    except Exception:
                        continue
                    price = price or (float(r["price"]) if r.get("price") else None)
                    g = 0.0
                    for f in ("call_gamma_oi", "put_gamma_oi", "call_gamma_vol", "put_gamma_vol"):
                        if r.get(f) not in (None, ""):
                            g += float(r[f])
                    rows.append((strike, g, r.get("time")))
                if price and rows and min(x[0] for x in rows) < price < max(x[0] for x in rows):
                    near = [x for x in rows if abs(x[0] - price) <= price * 0.015]
                    near.sort(key=lambda x: -abs(x[1]))
                    below = sum(x[1] for x in rows if price * 0.99 <= x[0] < price)
                    above = sum(x[1] for x in rows if price < x[0] <= price * 1.01)
                    when = et_time(rows[0][2])
                    o["spot_gamma"] = {
                        "price": price,
                        "as_of_et": when.strftime("%m-%d %H:%M") if when else None,
                        "top_strikes_within_1.5pct": [[s, round(g)] for s, g, _ in near[:4]],
                        "net_gamma_1pct_below": round(below), "net_gamma_1pct_above": round(above),
                        "status": "ok" if (when and when.date() == today) else "UNVERIFIED — stale timestamp",
                    }
                else:
                    o["spot_gamma"] = {"status": "UNVERIFIED — window does not bracket spot (paging artifact)"}
            else:
                o["spot_gamma"] = {"status": st}
            # expected move
            d, st = fetch(f"stock/{t}/interpolated-iv", hdr)
            if st == "ok" and isinstance(d, list):
                one = next((r for r in d if str(r.get("days")) in ("1", "1.0")), None) or \
                      min(d, key=lambda r: float(r.get("days", 999)))
                mv = one.get("implied_move_perc")
                # implied_move_perc is a fraction (0.005 = ±0.5%)
                ok = mv not in (None, "")
                o["expected_move_1d"] = {"fraction": mv, "pct_display": f"±{float(mv) * 100:.2f}%" if ok else None,
                                         "days": one.get("days"), "iv": one.get("volatility"),
                                         "status": "ok" if ok else "UNVERIFIED — no implied_move_perc"}
            else:
                o["expected_move_1d"] = {"status": st}
            # per-ticker net premium ticks since `since`
            d, st = fetch(f"stock/{t}/net-prem-ticks", hdr)
            if st == "ok" and isinstance(d, list):
                cp = pp = nd = 0.0; n = 0
                for r in d:
                    when = et_time(r.get("tape_time") or r.get("time") or r.get("timestamp"))
                    if not when or when.date() != today or when.time() < since:
                        continue
                    n += 1
                    cp += float(r.get("net_call_premium") or 0)
                    pp += float(r.get("net_put_premium") or 0)
                    nd += float(r.get("net_delta") or 0)
                o["net_premium_since"] = ({"ticks": n, "net_call_premium": round(cp), "net_put_premium": round(pp),
                                           "net_delta": round(nd), "status": "ok"} if n else
                                          {"status": "UNVERIFIED — no ticks today since the start time"})
            else:
                o["net_premium_since"] = {"status": st}
            out[t] = o
        # market tide
        d, st = fetch(f"market/market-tide?date={today}", hdr)
        if st == "ok" and isinstance(d, list):
            # tide values are cumulative for the session: subtract the last
            # bar before `since` so a 10:16 run reports only 10:00 onward
            timed = [(et_time(r.get("timestamp")), r) for r in d]
            timed = [(t, r) for t, r in timed if t and t.date() == today]
            before = [r for t, r in timed if t.time() < since]
            rows = [r for t, r in timed if t.time() >= since]
            if rows:
                first, last = rows[0], rows[-1]
                base_c = float(before[-1]["net_call_premium"]) if before else 0.0
                base_p = float(before[-1]["net_put_premium"]) if before else 0.0
                out["market_tide"] = {
                    "from_et": (et_time(before[-1]["timestamp"]) if before else et_time(first["timestamp"])).strftime("%H:%M"),
                    "to_et": et_time(last["timestamp"]).strftime("%H:%M"),
                    "net_call_premium": round(float(last["net_call_premium"]) - base_c),
                    "net_put_premium": round(float(last["net_put_premium"]) - base_p),
                    "status": "ok"}
            else:
                out["market_tide"] = {"status": "UNVERIFIED — no tide bars since the start time"}
        else:
            out["market_tide"] = {"status": st}
        # major headlines since `since`
        # The vendor's is_major flag is set on almost every press release
        # (dividend notices, earnings-date announcements — observed 2026-10-01),
        # so it is not a usable filter. Keep a headline only if it names a
        # tracked ticker or carries a macro / market keyword.
        d, st = fetch("news/headlines?limit=100", hdr)
        if st == "ok" and isinstance(d, list):
            tracked = set(TICKERS) | set(os.environ.get("FBC_TICKERS", "").split(","))
            macro = ("FED", "POWELL", "RATE", "YIELD", "TREASUR", "INFLATION", "CPI", "PCE",
                     "PAYROLL", "JOBS", "UNEMPLOYMENT", "TARIFF", "OIL", "CRUDE", "OPEC",
                     "IRAN", "ISRAEL", "HORMUZ", "STRIKE", "MISSILE", "CHINA", "TRUMP",
                     "SHUTDOWN", "S&P 500", "NASDAQ", "STOCKS", "HALT")
            heads = []
            for r in d:
                when = et_time(r.get("created_at") or r.get("time") or r.get("timestamp"))
                if not (when and when.date() == today and when.time() >= since):
                    continue
                text = (r.get("headline") or "").upper()
                tick = set(r.get("tickers") or [])
                if tick & tracked or any(k in text for k in macro):
                    heads.append({"et": when.strftime("%H:%M"), "headline": r.get("headline"),
                                  "tickers": r.get("tickers")})
            out["market_headlines"] = {"rows": heads[:15], "status": "ok",
                                       "note": "filtered by tracked tickers and macro keywords; is_major ignored"}
        else:
            out["market_headlines"] = {"status": st}
    finally:
        os.unlink(hdr)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
