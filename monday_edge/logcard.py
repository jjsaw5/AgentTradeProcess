"""Pre-registered Monday cards and their grading (CLAUDE.md §7 and §9).

`today` writes `log/<session>.json` + `.md` on its FIRST run of the day, before
the outcome exists, and never overwrites them. `grade` fills the outcome from
the real tape afterwards. The path off UNCALIBRATED is this log.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from analyze import ANALOG_TIERS
from sessions import compute_outcomes

ET = ZoneInfo("America/New_York")
SCORE_KEYS = ("fill_same_day", "fill_1h", "continuation")


def _f(x, digits=2, sign=True, pct=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    if pct:
        return f"{100 * x:.0f}%"
    return f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"


def _clean(v):
    if isinstance(v, (np.floating, float)):
        return None if not np.isfinite(v) else float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (date, datetime)):
        return str(v)
    return v


def _reference_tier(rows: list[dict]) -> dict | None:
    """The `gap size` tier is the reference rate; the category tiers inherit the feed-volume
    artifact recorded in the study's data notes."""
    for r in rows:
        if r["tier"] == "gap size":
            return r
    return rows[-1] if rows else None


def write_card(log_dir: Path, today: date, tag: dict, per_ticker: dict, analog_rows: dict, matches: dict,
               is_session: bool, force: bool = False) -> tuple[Path | None, Path | None]:
    """Write the pre-registered card. Returns (json_path, md_path); (None, None) if it already exists."""
    log_dir.mkdir(parents=True, exist_ok=True)
    jp, mp = log_dir / f"{today}.json", log_dir / f"{today}.md"
    if jp.exists() and not force:
        return None, None
    now = datetime.now(tz=ET)
    card = {
        "session": str(today),
        "prev": str(next(iter(per_ticker.values()))["prev"]) if per_ticker else None,
        "written_et": now.strftime("%Y-%m-%d %H:%M"),
        "pre_open": now.time() < datetime(2000, 1, 1, 9, 30).time(),
        "is_session": bool(is_session),
        "tag": {k: _clean(tag.get(k)) for k in ("category", "category_score", "risk_tone", "trump_mode",
                                                "n_headlines", "trump_market_posts", "tagger", "summary")},
        "tickers": {},
        "analogs": {},
        "confirmed_patterns_matching": [],
        "pre_registered": {"note": "Base rates from the `gap size` tier; scored at T+1 by `grade`. "
                                   "Confirmed patterns, if any, are listed and are the only claims of edge."},
        "outcome": None,
    }
    for t, info in per_ticker.items():
        card["tickers"][t] = {k: _clean(v) for k, v in info.items()}
        rows = analog_rows.get(t) or []
        card["analogs"][t] = [{k: _clean(v) for k, v in r.items()
                               if k in ("tier", "match", "n", "rate_fill_same_day", "rate_fill_1h", "median_min_to_fill",
                                        "rate_continuation", "mean_h0_ret", "mean_h4_ret")} for r in rows]
        ref = _reference_tier(rows)
        card["pre_registered"][t] = ({"fill_same_day_rate": _clean(ref["rate_fill_same_day"]),
                                      "fill_1h_rate": _clean(ref["rate_fill_1h"]),
                                      "continuation_rate": _clean(ref["rate_continuation"]),
                                      "reference_tier": f"{ref['tier']} (n={ref['n']})"} if ref else {})
        m = matches.get(t)
        if m is not None and len(m):
            for _, r in m.iterrows():
                card["confirmed_patterns_matching"].append({"ticker": t, "view": r["view"], "group": r["group"],
                                                            "signals": r["signals"], "implication": r["implication"]})
    jp.write_text(json.dumps(card, indent=2), encoding="utf-8")
    mp.write_text(_card_md(card), encoding="utf-8")
    return jp, mp


def _card_md(card: dict) -> str:
    L = [f"# Monday Edge — {card['session']} (pre-registered card)", "",
         f"**Written {card['written_et']} ET{' before the open' if card['pre_open'] else ' AFTER the open'}.** "
         "The outcome section is empty on purpose; `python run.py grade " + card["session"] + "` fills it "
         "from the real tape and nothing above it is rewritten afterwards.", ""]
    if not card["is_session"]:
        L += ["> Today does not follow a 3+ day break; analogs are post-weekend history and may not apply.", ""]
    tk = list(card["tickers"])
    L += ["## Inputs known before the open", "", "| | " + " | ".join(tk) + " |", "|---|" + "---|" * len(tk)]
    rows = [("Friday close", lambda i: _f(i.get("prev_close"), 2, sign=False)),
            ("Gap", lambda i: f"{_f(i.get('gap_pct'))}% ({i.get('gap_source')})"),
            ("Gap size / bucket", lambda i: f"{i.get('gap_size')} / {i.get('gap_bucket')}"),
            ("vs Friday implied 1-day move", lambda i: f"{i.get('em_bucket')} (EM1 {_f(i.get('em1_pct'), 2, sign=False)}%)"),
            ("Friday GEX / VIX", lambda i: f"{i.get('gex_regime')} / {i.get('vix_regime')}"),
            ("Tone vs gap", lambda i: str(i.get("tone_vs_gap")))]
    for label, fn in rows:
        L.append(f"| {label} | " + " | ".join(fn(card["tickers"][t]) for t in tk) + " |")
    tg = card["tag"]
    L += ["", f"Weekend tag ({tg.get('tagger')}): **{tg.get('category')}** (score {tg.get('category_score')}), "
              f"{tg.get('risk_tone')}, Trump {tg.get('trump_mode')}; {tg.get('n_headlines')} headlines, "
              f"{tg.get('trump_market_posts')} market-relevant posts."]
    if tg.get("summary"):
        L.append(f"Model summary (interpretation): {tg['summary']}")
    L.append("")
    if card["confirmed_patterns_matching"]:
        L += ["## Confirmed patterns that apply", ""]
        for m in card["confirmed_patterns_matching"]:
            L.append(f"- {m['ticker']} {m['view']} = {m['group']}: {m['signals']} → {m['implication']}")
    else:
        L += ["**Confirmed patterns that apply: none.** This card carries base rates, not an edge."]
    L.append("")
    for t in tk:
        L += [f"## Analogs — {t} (all history, narrowest → broadest)", "",
              "| tier | n | fill same day | fill 1st hr | median min to fill | close with gap | 0DTE | 4DTE |",
              "|---|---|---|---|---|---|---|---|"]
        for r in card["analogs"][t]:
            L.append(f"| {r['tier']} | {r['n']} | {_f(r['rate_fill_same_day'], pct=True)} | {_f(r['rate_fill_1h'], pct=True)} | "
                     f"{_f(r['median_min_to_fill'], 0, sign=False)} | {_f(r['rate_continuation'], pct=True)} | "
                     f"{_f(r['mean_h0_ret'])}% | {_f(r['mean_h4_ret'])}% |")
        L.append("")
    L += ["## Pre-registered scoring", "", "Scored at T+1 against the `gap size` tier (the category tiers inherit the "
          "feed-volume artifact in the study's data notes):", ""]
    for t in tk:
        p = card["pre_registered"].get(t) or {}
        if p:
            L.append(f"- {t}: fill same day {_f(p['fill_same_day_rate'], pct=True)}, fill 1st hr {_f(p['fill_1h_rate'], pct=True)}, "
                     f"close with gap {_f(p['continuation_rate'], pct=True)} — {p['reference_tier']}")
    L += ["", "One Monday grades nothing; the card exists so that the twelfth one can.", "", "## Outcome", "",
          "_Not yet graded._", ""]
    return "\n".join(L)


def grade_card(log_dir: Path, session: date, fmp, dry_run: bool = False, log=print) -> dict | None:
    """Fill the card's outcome from the real tape. Re-runnable: later runs add horizons as days close."""
    jp, mp = log_dir / f"{session}.json", log_dir / f"{session}.md"
    if not jp.exists():
        log(f"[grade] no card at {jp} — `today` writes one on its first run of the session day")
        return None
    card = json.loads(jp.read_text(encoding="utf-8"))
    prev = date.fromisoformat(card["prev"])
    now = datetime.now(tz=ET)
    outcome = {"graded_et": now.strftime("%Y-%m-%d %H:%M"), "tickers": {}}
    partial_today = now.date() == session and now.time() < datetime(2000, 1, 1, 16, 5).time()
    for t in card["tickers"]:
        daily = fmp.eod(t, prev - timedelta(days=12), session + timedelta(days=10), cache=False)
        intr = fmp.intraday_5m(t, session, cache=False)
        oc = compute_outcomes(daily, prev, session, intr)
        if not oc:
            log(f"[grade] {t}: no bars for {session} yet")
            continue
        horizons = sum(1 for k in range(5) if np.isfinite(oc.get(f"h{k}_ret", np.nan)))
        res = {k: _clean(oc.get(k)) for k in ("open", "gap_pct", "close_0", "fill_same_day", "fill_1h", "min_to_fill",
                                              "continuation", "first30_ret", "first30_holds", "orb_break", "orb_follow",
                                              "h0_ret", "h1_ret", "h2_ret", "h3_ret", "h4_ret", "h4_fill", "h0_mfe", "h0_mae")}
        res["horizons_closed"] = horizons
        res["partial_session"] = bool(partial_today)
        res["n_bars"] = int(len(intr))
        pre = card["pre_registered"].get(t) or {}
        res["scored_against"] = {k: pre.get(f"{k}_rate") for k in SCORE_KEYS}
        outcome["tickers"][t] = res
        log(f"[grade] {t}: open {oc['open']:.2f} (gap {oc['gap_pct']:+.2f}%), close {oc['close_0']:.2f}, "
            f"filled same day {oc['fill_same_day']} (base {_f(pre.get('fill_same_day_rate'), pct=True)}), "
            f"fill 1st hr {oc['fill_1h']} (base {_f(pre.get('fill_1h_rate'), pct=True)}), "
            f"min to fill {_f(oc['min_to_fill'], 0, sign=False)}, close with gap {oc['continuation']} "
            f"(base {_f(pre.get('continuation_rate'), pct=True)}), 0DTE {oc['h0_ret']:+.2f}%, "
            f"h4 {_f(oc.get('h4_ret'))}% [{horizons}/5 horizons closed{', PARTIAL SESSION' if partial_today else ''}]")
    if dry_run or not outcome["tickers"]:
        return outcome
    card["outcome"] = outcome
    jp.write_text(json.dumps(card, indent=2), encoding="utf-8")
    md = mp.read_text(encoding="utf-8") if mp.exists() else ""
    head = md.split("## Outcome")[0] if "## Outcome" in md else md
    lines = [head.rstrip(), "", "## Outcome", "", f"Graded {outcome['graded_et']} ET"
             + (" — **partial session, regrade after the close**" if partial_today else "") + ".", "",
             "| | " + " | ".join(outcome["tickers"]) + " |", "|---|" + "---|" * len(outcome["tickers"])]
    def row(label, fn):
        lines.append(f"| {label} | " + " | ".join(fn(r) for r in outcome["tickers"].values()) + " |")
    row("Open / gap", lambda r: f"{_f(r['open'], 2, sign=False)} / {_f(r['gap_pct'])}%")
    row("Filled same day (base)", lambda r: f"{'yes' if r['fill_same_day'] else 'no'} ({_f(r['scored_against']['fill_same_day'], pct=True)})")
    row("Filled in 1st hour (base)", lambda r: f"{'yes' if r['fill_1h'] else 'no'} ({_f(r['scored_against']['fill_1h'], pct=True)})")
    row("Minutes to fill", lambda r: _f(r["min_to_fill"], 0, sign=False))
    row("Closed with gap (base)", lambda r: f"{'yes' if r['continuation'] else 'no'} ({_f(r['scored_against']['continuation'], pct=True)})")
    row("First 30m held", lambda r: str(r["first30_holds"]))
    row("ORB break / followed", lambda r: f"{r['orb_break']} / {r['orb_follow']}")
    row("0DTE / 1DTE / 2DTE / 4DTE %", lambda r: " / ".join(_f(r[f"h{k}_ret"]) for k in (0, 1, 2, 4)))
    row("0DTE MFE / MAE %", lambda r: f"{_f(r['h0_mfe'], 2, sign=False)} / {_f(r['h0_mae'], 2, sign=False)}")
    row("Horizons closed", lambda r: f"{r['horizons_closed']}/5")
    lines += ["", "Returns are underlying moves with the gap positive, not option P&L.", ""]
    mp.write_text("\n".join(lines), encoding="utf-8")
    log(f"[grade] wrote {jp} and {mp}")
    return outcome
