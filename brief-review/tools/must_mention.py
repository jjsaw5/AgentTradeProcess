#!/usr/bin/env python3
"""Regenerate brief-review/MUST_MENTION.md from the scoring database.

Computes the names the next morning brief may not one-liner, per the three
ratified coverage rules:
  I-4 fragility floor   — |move| >= 5% last session, or |net| >= 15% over the
                          trailing 3 sessions (from watchlist_events.move_pct)
  I-7 active complex    — complexes with any member +/-5% within the last 2
                          recorded sessions (deactivation is a human edit to
                          the complexes table, flagged here when due)
  I-2 accumulation      — same non-'none'/'mixed' flow lean in >= 3
                          consecutive briefs (from flow_observations)

Data coverage note: move_pct comes from graded reviews (T+1). A name with no
row on a date is treated as no-data (NA_no_data), never as 0.0. The output
file states its data-through date; the brief spec says what to do if stale.

Credentials: TURSO_URL / TURSO_TOKEN from env or the repo's gitignored .env.
Usage:  must_mention.py            # writes brief-review/MUST_MENTION.md
        must_mention.py --stdout   # print instead of write
"""
import json, os, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "brief-review", "MUST_MENTION.md")


def env():
    if not (os.environ.get("TURSO_URL") and os.environ.get("TURSO_TOKEN")):
        envfile = os.path.join(REPO, ".env")
        if os.path.exists(envfile):
            for line in open(envfile):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ.setdefault(k, v)
    u, t = os.environ.get("TURSO_URL"), os.environ.get("TURSO_TOKEN")
    if not (u and t):
        sys.exit("TURSO_URL / TURSO_TOKEN not set (env or gitignored .env)")
    return u, t


def query(sql_statements):
    u, t = env()
    reqs = [{"type": "execute", "stmt": {"sql": s}} for s in sql_statements]
    reqs.append({"type": "close"})
    p = subprocess.run(
        ["curl", "-sS", "--fail-with-body", "-m", "60", "--retry", "3",
         "--retry-delay", "2", "--retry-all-errors", "-X", "POST",
         u + "/v2/pipeline", "-H", "Authorization: Bearer " + t,
         "-H", "Content-Type: application/json", "--data-binary", "@-"],
        input=json.dumps({"requests": reqs}).encode(), capture_output=True)
    if p.returncode != 0:
        sys.exit("FETCH FAILED: " + p.stderr.decode())
    out = json.loads(p.stdout)
    results = []
    for r in out["results"][:-1]:
        if r["type"] == "error":
            sys.exit("SQL ERROR: " + json.dumps(r["error"]))
        res = r["response"]["result"]
        cols = [c["name"] for c in res["cols"]]
        results.append([dict(zip(cols, [c.get("value") for c in row]))
                        for row in res["rows"]])
    return results


def main():
    moves, flows, complexes = query([
        "SELECT brief_date, ticker, move_pct FROM watchlist_events "
        "WHERE move_pct IS NOT NULL ORDER BY brief_date",
        "SELECT brief_date, ticker, lean, note FROM flow_observations "
        "ORDER BY ticker, brief_date",
        "SELECT complex_name, ticker FROM complexes WHERE deactivated IS NULL",
    ])
    dates = sorted({m["brief_date"] for m in moves})
    if not dates:
        sys.exit("no graded sessions in watchlist_events")
    last, last3 = dates[-1], dates[-3:]
    by_td = {(m["brief_date"], m["ticker"]): float(m["move_pct"]) for m in moves}
    tickers = sorted({m["ticker"] for m in moves})

    reasons = {}  # ticker -> [reason, ...]

    # I-4a: prior-session +/-5%
    for t in tickers:
        mv = by_td.get((last, t))
        if mv is not None and abs(mv) >= 5:
            reasons.setdefault(t, []).append(
                f"I-4: moved {mv:+.1f}% last session ({last})")
    # I-4b: net +/-15% over trailing 3 sessions (needs all 3 present)
    for t in tickers:
        ms = [by_td.get((d, t)) for d in last3]
        if len(last3) == 3 and all(m is not None for m in ms):
            net = 1.0
            for m in ms:
                net *= 1 + m / 100
            net = (net - 1) * 100
            if abs(net) >= 15:
                reasons.setdefault(t, []).append(
                    f"I-4: net {net:+.1f}% over 3 sessions ({last3[0]}..{last})")

    # I-7: active complexes — any member +/-5% within the last 2 sessions
    cx = {}
    for row in complexes:
        cx.setdefault(row["complex_name"], []).append(row["ticker"])
    for name, members in cx.items():
        recent = [by_td.get((d, t)) for d in dates[-2:] for t in members]
        hot = [m for m in recent if m is not None and abs(m) >= 5]
        if hot:
            for t in members:
                reasons.setdefault(t, []).append(
                    f"I-7: '{name}' complex active (a member moved "
                    f"{max(hot, key=abs):+.1f}% within last 2 sessions)")
        else:
            for t in members:
                reasons.setdefault(t, []).append(
                    f"I-7: '{name}' complex — no member ±5% in last 2 "
                    f"sessions: deactivation due (edit complexes table)")

    # I-2: >= 3 consecutive briefs with the same directional lean
    seq = {}
    for f in flows:
        seq.setdefault(f["ticker"], []).append((f["brief_date"], f["lean"]))
    for t, obs in seq.items():
        obs.sort()
        tail = [lean for _, lean in obs]
        streak, lean0 = 0, None
        for lean in reversed(tail):
            if lean in ("bull", "bear") and (lean0 is None or lean == lean0):
                lean0, streak = lean, streak + 1
            else:
                break
        if streak >= 3:
            reasons.setdefault(t, []).append(
                f"I-2: {lean0} flow lean in {streak} consecutive briefs — "
                f"ESCALATE TO FLAGGED, quantify the cumulative build")

    lines = [
        "# MUST-MENTION — floor coverage for the next brief run",
        "",
        f"Generated {os.environ.get('MM_TODAY', 'by must_mention.py')} from the",
        f"scoring database. **Data through graded session {last}.** If that is",
        "more than one trading day behind, apply spec rules I-2/I-4/I-7 by hand",
        "and say so in §13. Names below may NOT receive a bare \"nothing",
        "notable\" one-liner; each needs at least the sentence its rule",
        "requires (see daily-market-brief/SKILL.md §6A). This is a floor, not",
        "a ceiling. A name with no coverage row is NA_no_data, not cleared.",
        "",
        "| Ticker | Reason(s) |",
        "|---|---|",
    ]
    for t in sorted(reasons):
        lines.append(f"| {t} | " + " · ".join(reasons[t]) + " |")
    if not reasons:
        lines.append("| — | No names trip I-2/I-4/I-7 on current data. |")
    text = "\n".join(lines) + "\n"

    if "--stdout" in sys.argv:
        print(text)
    else:
        with open(OUT, "w") as f:
            f.write(text)
        print(f"wrote {OUT} ({len(reasons)} names, data through {last})")


if __name__ == "__main__":
    main()
