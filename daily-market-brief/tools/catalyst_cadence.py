#!/usr/bin/env python3
"""
Product & corporate catalyst cadence detector — feeds daily-market-brief §4B.

WHY THIS EXISTS
  2026-09-09: META gapped +5.2% premarket on the launch of "Muse", its personal AI
  agent. The product line had been shipping since 8/05 and the stock had paid for
  three prior releases (+2.5%, +3.0%, +1.0%). The brief had no section that could
  see any of it: every non-biotech catalyst path is either calendar-driven
  (§3, §4) or reactive (§5, §6, §10), so the first the brief knew was the gap.

WHAT IT DOES
  For each ticker, pulls recent headlines and finds terms that are running
  unusually hot versus that ticker's OWN multi-week baseline. It does not use a
  keyword list — a keyword approach was tested against this exact case on
  2026-09-09 and caught ZERO (see §4B in SKILL.md for the backtest). Recurring
  product codenames surface on frequency alone.

  Each flagged day is paired with the stock's actual close-to-close reaction, so
  a repeating theme can be judged by whether the market has been paying for it.

HONESTY (CLAUDE.md §3)
  - A failed fetch is reported as a failure, never as "no catalysts found."
    Absence of a measurement is not a measurement of absence.
  - Term spikes are ATTENTION, not verified events. Every hit must be read
    before it is reported; the tool surfaces candidates, a human/agent confirms.
  - UNCALIBRATED: validated against one episode (META/Muse). See §4B limits.

USAGE
  python3 catalyst_cadence.py --tickers META,GOOGL,NVDA --days 45
  python3 catalyst_cadence.py --tickers META --days 45 --asof 2026-09-08
"""
import os, sys, json, re, argparse, urllib.request, urllib.error
import datetime as dt
from collections import Counter, defaultdict

FMP = "https://financialmodelingprep.com"

# 13F / holdings / analyst-listicle spam. Roughly 20% of a mega-cap's feed.
NOISE = re.compile(r"""(
  \bshares\s+(sold|bought|purchased|acquired)\b|\bholdings?\b|\b13F\b|\bstake\s+in\b
 |\bposition\s+in\s+\w|\b(raises?|lowers?|boosts?|trims?|cuts?|reduces?|increases?|decreases?|has|had)\s+
   (a\s+|its\s+|new\s+)?\$?[\d.,]*\s*(million|billion)?\s*(stock\s+)?position\b
 |\b(acquires?|purchases?|sells?|buys?)\s+([\d,]+|new\s+)?\s*shares\b
 |\bstock\s+(holdings|position)\b|\bshould\s+you\s+buy\b|\bis\s+it\s+time\s+to\s+buy\b
 |\breasons\s+to\b|\bbest\s+stock\b|\bmotley\b|\bzacks\b|\bGF\s+Score\b
 |\bundervalued\s+--|\bmagnificent\s+seven\b|\bmag\s+7\b)""", re.I | re.X)

STOP = set("""the a an and or of to in for on at by with from as is are was were be been being will would could
should shall may might must can meta platforms inc corp corporation stock stocks shares share market markets
this that these those it its their they them what why how who when where new now more most than then but not
you your we our us if said says say after before over under up down out about into just still here there
also than very much many some any one two three first next last year years day days week weeks month months
company companies report reports reported according amid despite while during into onto off big small high low""".split())

TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9'\-]{2,}")


def fetch(url, what):
    """Fetch JSON. Raises on failure — callers must not swallow into 'no data'."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        raise RuntimeError(f"FETCH FAILED [{what}]: {e}") from e


def headlines(tick, frm, to, key):
    rows, seen, out = [], set(), []
    for page in range(0, 8):
        u = f"{FMP}/stable/news/stock?symbols={tick}&from={frm}&to={to}&limit=100&page={page}&apikey={key}"
        d = fetch(u, f"news/{tick}/p{page}")
        if not isinstance(d, list) or not d:
            break
        rows += d
    for a in rows:
        t = (a.get("title") or "").strip()
        k = (a.get("publishedDate", ""), t)
        if not t or k in seen:
            continue
        seen.add(k)
        if NOISE.search(t):
            continue
        out.append({"date": a.get("publishedDate", "")[:10],
                    "ts": a.get("publishedDate", "")[:16],
                    "title": t,
                    "site": a.get("site", "")})
    return out


def reactions(tick, frm, to, key):
    d = fetch(f"{FMP}/stable/historical-price-eod/full?symbol={tick}&from={frm}&to={to}&apikey={key}",
              f"eod/{tick}")
    if not isinstance(d, list) or not d:
        return {}
    d = sorted(d, key=lambda r: r["date"])
    out = {}
    for i, r in enumerate(d):
        prev = d[i - 1]["close"] if i else r["close"]
        out[r["date"]] = {"close": r["close"],
                          "chg": (r["close"] - prev) / prev * 100 if i else 0.0,
                          "gap": (r["open"] - prev) / prev * 100 if i else 0.0}
    return out


def spikes(arts, min_articles=5, min_ratio=3.0, min_share=0.15, min_count=2):
    """Terms over-represented on a day vs their share across the whole window."""
    base, byday, n_day = Counter(), defaultdict(Counter), defaultdict(int)
    for a in arts:
        ws = {w.lower() for w in TOKEN.findall(a["title"])}
        ws = {w for w in ws if w not in STOP and len(w) > 3}
        base.update(ws); byday[a["date"]].update(ws); n_day[a["date"]] += 1
    N = len(arts)
    hits = {}
    for day, cnt in byday.items():
        n = n_day[day]
        if n < min_articles:
            continue
        found = []
        for w, c in cnt.items():
            if c < min_count:
                continue
            b = base[w] / N
            share = c / n
            if b > 0 and share / b >= min_ratio and share >= min_share:
                found.append((share / b, w, c))
        if found:
            hits[day] = sorted(found, reverse=True)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", required=True)
    ap.add_argument("--days", type=int, default=45, help="baseline window length")
    ap.add_argument("--recent", type=int, default=5, help="report spikes inside the last N days")
    ap.add_argument("--asof", default=None, help="YYYY-MM-DD (backtesting); default today")
    ap.add_argument("--all", action="store_true", help="report every spike in the window")
    ap.add_argument("--include-nontrading", action="store_true",
                    help="also report spikes on days with no session (weekends/holidays). "
                         "Off by default: those days carry almost only opinion/listicle "
                         "content and generated pure noise in the 2026-09-09 test run.")
    a = ap.parse_args()

    key = os.environ.get("FMP_API_KEY")
    if not key or len(key) < 20:
        print("FMP_API_KEY missing or too short — DATA SOURCE FAILED, not 'no catalysts'.",
              file=sys.stderr)
        return 2

    to = dt.date.fromisoformat(a.asof) if a.asof else dt.date.today()
    frm = to - dt.timedelta(days=a.days)
    cutoff = (to - dt.timedelta(days=a.recent)).isoformat()

    failures = []
    for tick in [t.strip().upper() for t in a.tickers.split(",") if t.strip()]:
        try:
            arts = headlines(tick, frm.isoformat(), to.isoformat(), key)
            rx = reactions(tick, frm.isoformat(), to.isoformat(), key)
        except RuntimeError as e:
            failures.append(f"{tick}: {e}")
            print(f"\n=== {tick} — UNVERIFIED, data source failed ===\n    {e}")
            continue
        if not arts:
            print(f"\n=== {tick} — NA_no_data (feed returned no usable headlines) ===")
            continue

        hits = spikes(arts)
        shown = {d: v for d, v in hits.items() if a.all or d >= cutoff}
        if not a.include_nontrading:
            # No EOD row == no session that day. Reaction is unmeasurable and the
            # feed is dominated by weekend opinion pieces.
            shown = {d: v for d, v in shown.items() if d in rx}
        print(f"\n=== {tick} — {len(arts)} headlines over {a.days}d, "
              f"{len(hits)} spike-days ({len(shown)} in window) ===")
        if not shown:
            print("    No unusual theme concentration in the reporting window.")
            continue
        for day in sorted(shown):
            terms = shown[day][:5]
            r = rx.get(day)
            react = (f"close {r['chg']:+.2f}%  (gap {r['gap']:+.2f}%)" if r
                     else "reaction NA_no_data (non-trading day)")
            print(f"\n  {day}   {react}")
            print("    terms: " + ", ".join(f"{w} (x{ratio:.0f} baseline, {c} articles)"
                                            for ratio, w, c in terms))
            key_terms = {w for _, w, _ in terms}
            for art in sorted(arts, key=lambda x: x["ts"]):
                if art["date"] != day:
                    continue
                if {w.lower() for w in TOKEN.findall(art["title"])} & key_terms:
                    print(f"      {art['ts'][11:]}  {art['title'][:100]}")

    if failures:
        print(f"\n{len(failures)} ticker(s) FAILED to fetch — report as UNVERIFIED, "
              f"never as 'no catalysts found'.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
