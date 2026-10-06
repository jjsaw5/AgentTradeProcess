#!/usr/bin/env python3
"""Record daily 0DTE / 1DTE option marks for SPY and QQQ (owner-directed 2026-10-06).

Feeds options-expert/log/marks/option_marks.csv, the data for the time-exit study
(options-expert/log/studies/2026-10-06-time-exit/PREREG.md). Read-only: it parses saved
Robinhood MCP responses; it never calls a brokerage API and never places anything.

Two steps, run by the evening brief review (brief-review/SKILL.md, "Option marks"):

  plan   --date D --equity-file F
         F = saved get_equity_historicals response, 5-minute bars, SPY+QQQ, covering 9:30-16:00 ET of D.
         Prints, per symbol: 9:30 open, 9:45 price, first-bar side, ATM strike (nearest $1), and the
         two expiries to look up (D and the next weekday; pass --next-expiry if that is a holiday).

  record --date D --equity-file F --option-file G [--option-file H ...]
         G = saved get_option_historicals response(s), 5-minute bars, for the call AND put at the
         ATM strike, both expiries, both symbols (8 contracts). Contract identity is read from each
         result's occ_symbol. Appends one row per contract. Refuses duplicates.

Marks are the close of the 5-minute bar ending at each checkpoint (last trade, not bid/ask).
An interpolated bar (no trade) is written as NA_no_data, never filled (CLAUDE.md §4).
"""
import argparse, csv, json, os, sys
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
CSV = os.path.join(os.path.dirname(__file__), "..", "log", "marks", "option_marks.csv")
CHECKPOINTS = ["09:45", "10:15", "10:45", "11:00", "12:00", "14:00", "15:30"]  # bar ENDING at this time
FIELDS = (["date", "symbol", "open_0930", "u_0945", "first_bar_side", "strike", "expiry", "dte", "type", "occ"]
          + [f"m_{c.replace(':', '')}" for c in CHECKPOINTS]
          + [f"u_{c.replace(':', '')}" for c in CHECKPOINTS[1:]]
          + ["hi_0945_1530", "lo_0945_1530", "na_marks", "recorded_at"])
NA = "NA_no_data"
SYMBOLS = ("SPY", "QQQ")


def load_results(path):
    with open(path) as fh:
        d = json.load(fh)
    return d["data"]["results"]


def bars_et(result, day):
    """{bar_start 'HH:MM' ET: (o, h, l, c) or None if interpolated} for one trading day."""
    out = {}
    for b in result["bars"]:
        t = datetime.fromisoformat(b["begins_at"].replace("Z", "+00:00")).astimezone(NY)
        if t.date() != day:
            continue
        key = t.strftime("%H:%M")
        out[key] = None if b.get("interpolated") else tuple(float(b[k]) for k in ("open_price", "high_price", "low_price", "close_price"))
    return out


def bar_start_for(checkpoint):
    t = datetime.strptime(checkpoint, "%H:%M") - timedelta(minutes=5)
    return t.strftime("%H:%M")


def underlying(equity_file, day):
    res = {}
    for r in load_results(equity_file):
        if r["symbol"] not in SYMBOLS:
            continue
        b = bars_et(r, day)
        if "09:30" not in b or b["09:30"] is None:
            sys.exit(f"{r['symbol']}: no real 9:30 bar on {day} — wrong file or date (a 200 is not a success)")
        open_ = b["09:30"][0]
        p945 = b[bar_start_for("09:45")][3]
        move = (p945 - open_) / open_
        side = "flat" if abs(move) < 0.0002 else ("call" if move > 0 else "put")
        path = {c: (b.get(bar_start_for(c)) or (None,) * 4)[3] for c in CHECKPOINTS}
        window = [v for k, v in b.items() if v and "09:45" <= k < "15:30"]
        res[r["symbol"]] = dict(open=open_, p945=p945, side=side, strike=round(p945), path=path,
                                hi=max(v[1] for v in window), lo=min(v[2] for v in window))
    return res


def next_weekday(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def parse_occ(occ):
    s = occ.replace(" ", "")
    i = next(k for k, ch in enumerate(s) if ch.isdigit())
    root, rest = s[:i], s[i:]
    exp = datetime.strptime(rest[:6], "%y%m%d").date()
    typ = "call" if rest[6] == "C" else "put"
    strike = int(rest[7:]) / 1000
    return root, exp, typ, strike


def fmt(x):
    return NA if x is None else f"{x:.4f}".rstrip("0").rstrip(".")


def cmd_plan(a):
    day = date.fromisoformat(a.date)
    nxt = a.next_expiry or next_weekday(day).isoformat()
    for sym, u in underlying(a.equity_file, day).items():
        print(f"{sym}: open {u['open']:.2f} · 9:45 {u['p945']:.2f} · first bar {u['side']} · ATM strike {u['strike']} "
              f"· look up call+put at {u['strike']} for expiries {day.isoformat()},{nxt}")


def cmd_record(a):
    day = date.fromisoformat(a.date)
    und = underlying(a.equity_file, day)
    existing = set()
    if os.path.exists(CSV):
        with open(CSV) as fh:
            existing = {(r["date"], r["occ"]) for r in csv.DictReader(fh)}
    rows = []
    for f in a.option_file:
        for r in load_results(f):
            occ = r["occ_symbol"].replace(" ", "")
            root, exp, typ, strike = parse_occ(occ)
            u = und.get(root)
            if u is None:
                sys.exit(f"{occ}: no underlying bars for {root}")
            if strike != u["strike"]:
                sys.exit(f"{occ}: strike {strike} is not the 9:45 ATM strike {u['strike']} — wrong contract")
            if (a.date, occ) in existing:
                print(f"skip duplicate {occ}")
                continue
            dte = "0DTE" if exp == day else "1DTE"
            b = bars_et(r, day)
            marks = [(b.get(bar_start_for(c)) or (None,) * 4)[3] for c in CHECKPOINTS]
            row = dict(date=a.date, symbol=root, open_0930=fmt(u["open"]), u_0945=fmt(u["p945"]),
                       first_bar_side=u["side"], strike=fmt(strike), expiry=exp.isoformat(), dte=dte, type=typ, occ=occ,
                       hi_0945_1530=fmt(u["hi"]), lo_0945_1530=fmt(u["lo"]),
                       na_marks=sum(m is None for m in marks),
                       recorded_at=datetime.now(NY).strftime("%Y-%m-%d %H:%M ET"))
            for c, m in zip(CHECKPOINTS, marks):
                row[f"m_{c.replace(':', '')}"] = fmt(m)
            for c in CHECKPOINTS[1:]:
                row[f"u_{c.replace(':', '')}"] = fmt(u["path"][c])
            rows.append(row)
    if len(rows) not in (0, 8) and not a.allow_partial:
        sys.exit(f"expected 8 contracts (2 symbols x call/put x 0DTE/1DTE), got {len(rows)} — pass --allow-partial to write anyway")
    new = not os.path.exists(CSV)
    os.makedirs(os.path.dirname(CSV), exist_ok=True)
    with open(CSV, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['date']} {r['occ']:24} {r['dte']} 9:45 {r['m_0945']:>8}  NA={r['na_marks']}")
    print(f"wrote {len(rows)} rows -> {os.path.normpath(CSV)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan"); pl.add_argument("--date", required=True); pl.add_argument("--equity-file", required=True)
    pl.add_argument("--next-expiry", help="override the 1DTE expiry (holidays)")
    rc = sub.add_parser("record"); rc.add_argument("--date", required=True); rc.add_argument("--equity-file", required=True)
    rc.add_argument("--option-file", action="append", required=True); rc.add_argument("--allow-partial", action="store_true")
    a = p.parse_args()
    {"plan": cmd_plan, "record": cmd_record}[a.cmd](a)


if __name__ == "__main__":
    main()
