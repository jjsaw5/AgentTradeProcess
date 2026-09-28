#!/usr/bin/env python3
"""Monday Edge CLI.

    python run.py study [--mock] [--llm] [--start YYYY-MM-DD] [--seed N]
    python run.py today [--mock] [--llm] [--gap SPY=0.45 --gap QQQ=0.70]

Nothing here trades. Brokerage access is read-only everywhere in this repo;
this tool does not even reach a brokerage — it reads FMP and Unusual Whales.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from analyze import analogs, analyze, matching_confirmed
from build import build_dataset
from config import settings
from sessions import (em_bucket, gap_bucket, gap_size, gex_regime, lookup_on_or_before, news_window,
                      vix_regime)
from tagger import tag_weekend, tone_vs_gap

ET = ZoneInfo("America/New_York")
UTC = timezone.utc

if hasattr(sys.stdout, "reconfigure"):  # Windows cp1252 guard (PLAYBOOK §4 lesson)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def log(msg: str) -> None:
    print(msg, flush=True)


def _setup(args):
    cfg = settings(start=getattr(args, "start", None))
    if args.mock:
        from mock_data import MockWorld
        world = MockWorld(seed=args.seed)
        cfg.start_date = world.start if not getattr(args, "start", None) else cfg.start_date
        cfg.out_dir = cfg.out_dir / "mock"
        cfg.cache_dir = cfg.cache_dir / "mock"
        fmp, uw = world.clients()
    else:
        from clients import make_clients
        if not cfg.fmp_api_key:
            sys.exit("FMP_API_KEY is not set (put it in monday_edge/.env — see .env.example)")
        fmp, uw = make_clients(cfg)
    cfg.ensure_dirs()
    return cfg, fmp, uw


def cmd_study(args) -> int:
    cfg, fmp, uw = _setup(args)
    df, notes = build_dataset(fmp, uw, cfg, use_llm=args.llm, log=log, workers=args.workers)
    an = analyze(df, cfg)
    from report import study_report
    pat_path = cfg.out_dir / "patterns.csv"
    an.patterns.to_csv(pat_path, index=False)
    html_path = cfg.out_dir / "study_report.html"
    html_path.write_text(study_report(an, df, notes, cfg), encoding="utf-8")
    log(f"[study] {an.n_sessions} sessions {an.date_range[0]} → {an.date_range[1]}, holdout from {an.cut_date}")
    for t in cfg.tickers:
        log(f"[study] {t}: {an.n_tests.get(t, 0)} eligible tests, ≈{an.expected_flukes.get(t, 0):.1f} expected flukes")
    conf = an.confirmed
    if conf.empty:
        log("[study] confirmed patterns: none (a valid result)")
    else:
        log(f"[study] confirmed patterns: {len(conf)}")
        for _, r in conf.iterrows():
            log(f"  {r['ticker']:4} {r['view']:22} {r['group']:28} n={int(r['n_disc'])}/{int(r['n_hold'])}  {r['signals']}  → {r['implication']}")
    log(f"[study] wrote {html_path} and {pat_path}")
    return 0


def _parse_gaps(items) -> dict:
    out = {}
    for it in items or []:
        if "=" not in it:
            sys.exit(f"--gap expects TICKER=PCT, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip().upper()] = float(v)
    return out


def cmd_today(args) -> int:
    cfg, fmp, uw = _setup(args)
    wk_path = cfg.out_dir / "weekends.csv"
    if not wk_path.is_file():
        sys.exit(f"{wk_path} not found — run `python run.py study{' --mock' if args.mock else ''}` first")
    df = pd.read_csv(wk_path)
    df["session"] = pd.to_datetime(df["session"]).dt.date
    an = analyze(df, cfg)

    today = date.today()
    now = datetime.now(tz=UTC)
    tickers = list(cfg.tickers)
    daily = {t: fmp.eod(t, today - timedelta(days=30), today) for t in tickers}
    vix = fmp.eod("^VIX", today - timedelta(days=30), today)
    past = daily[tickers[0]][daily[tickers[0]]["date"] < today]
    if past.empty:
        sys.exit("no prior trading day found in daily bars")
    prev = past["date"].iloc[-1]
    w_start, w_end = news_window(prev, today)
    w_end = min(w_end, now)
    is_session = (today - prev).days >= 3
    log(f"[today] {today} — prev trading day {prev} ({(today - prev).days} calendar days); window {w_start:%Y-%m-%d %H:%M} → {w_end:%Y-%m-%d %H:%M} UTC")
    if not is_session:
        log("[today] NOTE: today does not follow a 3+ day break; analogs are post-weekend history and may not apply")

    headlines = fmp.news(w_start, w_end, symbols=tuple(tickers), cache=False)
    uw_heads = uw.headlines(w_start, cache=False) if uw.enabled else []
    seen = {h["title"].lower() for h in headlines}
    for h in uw_heads:
        ts = datetime.fromisoformat(h["published_utc"])
        if h["title"].lower() not in seen and w_start <= ts < w_end:
            headlines.append(h)
            seen.add(h["title"].lower())
    headlines.sort(key=lambda h: h["published_utc"])
    posts = uw.potus_posts(w_start, cache=False) if uw.enabled else []
    posts = [p for p in posts if w_start <= datetime.fromisoformat(p["ts_utc"]) < w_end]
    tag = tag_weekend(headlines, posts, cfg, use_llm=args.llm)
    log(f"[today] {len(headlines)} headlines, {len(posts)} posts → category={tag['category']} (score {tag['category_score']:.0f}), "
        f"tone={tag['risk_tone']}, trump={tag['trump_mode']}")
    if tag.get("summary"):
        log(f"[today] summary: {tag['summary']}")

    manual = _parse_gaps(args.gap)
    pre_open = now.astimezone(ET).time() < datetime(2000, 1, 1, 9, 30).time()
    per_ticker, analog_rows, matches = {}, {}, {}
    for t in tickers:
        d = daily[t]
        prev_row = d[d["date"] == prev]
        prev_close = float(prev_row["close"].iloc[0]) if len(prev_row) else np.nan
        if t in manual:
            gap, src = manual[t], "manual"
        else:
            if pre_open:
                pm = fmp.premarket(t)
                px, src = pm.get("price"), "pre-market quote (bid/ask mid)"
            else:
                q = fmp.quote(t)
                px, src = q.get("open") or q.get("price"), "open"
            try:
                px = float(px)
            except (TypeError, ValueError):
                px = np.nan
            gap = (px / prev_close - 1.0) * 100.0 if np.isfinite(px) and np.isfinite(prev_close) and prev_close > 0 else np.nan
            if not np.isfinite(gap):
                src = "UNVERIFIED (no quote)"
        em = uw.implied_moves(t, prev) if uw.enabled else {}
        gex = uw.greek_exposure(t) if uw.enabled else None
        regime, net_g, pctile = gex_regime(gex, prev)
        vix_p = lookup_on_or_before(vix, prev, "close")
        gb = gap_bucket(gap, cfg.gap_flat, cfg.gap_large)
        pos = d.reset_index(drop=True)
        ip = pos.index[pos["date"] == prev]
        pw = np.nan
        if len(ip) and ip[0] >= 5:
            pw = (pos["close"].iloc[ip[0]] / pos["close"].iloc[ip[0] - 5] - 1.0) * 100.0
        attrs = {
            "category": tag["category"], "trump_mode": tag["trump_mode"],
            "gap_size": gap_size(gap, cfg.gap_flat, cfg.gap_large), "gap_bucket": gb,
            "em_bucket": em_bucket(gap, em.get(1)), "vix_regime": vix_regime(vix_p), "gex_regime": regime,
            "tone_vs_gap": tone_vs_gap(tag["risk_tone"], gb),
            "prior_week_dir_vs_gap": ("same" if np.isfinite(pw) and np.isfinite(gap) and ((pw >= 0) == (gap >= 0))
                                      else ("opposite" if np.isfinite(pw) and np.isfinite(gap) else "n/a")),
        }
        per_ticker[t] = {"gap_pct": gap, "gap_source": src, "prev": prev, "prev_close": prev_close,
                         "em1_pct": em.get(1, np.nan), "gex_pctile": pctile, **attrs}
        analog_rows[t] = analogs(df, t, attrs)
        matches[t] = matching_confirmed(an, t, attrs)
        log(f"\n[today] {t}: gap {gap:+.2f}% ({src}), {attrs['gap_size']} / {gb} / {attrs['em_bucket']}; Friday close {prev_close:.2f}, "
            f"EM1 {em.get(1, float('nan')):.2f}%, GEX {regime}, VIX {attrs['vix_regime']}")
        log(f"  {'tier':36} {'n':>4} {'fill':>6} {'fill1h':>6} {'mtf':>5} {'cont':>6} {'0DTE':>7} {'4DTE':>7}")
        for r in analog_rows[t]:
            mtf = r["median_min_to_fill"]
            log(f"  {r['tier']:36} {r['n']:4d} {100 * r['rate_fill_same_day']:5.0f}% {100 * r['rate_fill_1h']:5.0f}% "
                f"{(f'{mtf:4.0f}' if np.isfinite(mtf) else '   —'):>5} {100 * r['rate_continuation']:5.0f}% "
                f"{r['mean_h0_ret']:+6.2f}% {r['mean_h4_ret']:+6.2f}%")
        m = matches[t]
        if m.empty:
            log("  confirmed patterns matching today: none")
        else:
            for _, r in m.iterrows():
                log(f"  MATCH {r['view']} = {r['group']} (n {int(r['n_disc'])}/{int(r['n_hold'])}): {r['signals']} → {r['implication']}")

    from report import today_brief
    out = cfg.out_dir / f"brief_{today}.html"
    out.write_text(today_brief(today, (w_start, w_end), tag, per_ticker, analog_rows, matches, headlines, is_session, cfg),
                   encoding="utf-8")
    log(f"\n[today] caution: n under ~15 is an anecdote; wait out the first 30 minutes on a fill thesis; size by Playbook gates.")
    log(f"[today] wrote {out}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Monday Edge: post-weekend gap study for SPY/QQQ")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("study", help="build history, find patterns, write the HTML report")
    s.add_argument("--mock", action="store_true", help="use the synthetic world instead of live APIs")
    s.add_argument("--llm", action="store_true", help="tag weekends with the Anthropic model (needs ANTHROPIC_API_KEY)")
    s.add_argument("--start", help="override START_DATE (YYYY-MM-DD)")
    s.add_argument("--seed", type=int, default=42, help="mock world seed")
    s.add_argument("--workers", type=int, default=3, help="parallel sessions during the build (API rate limits permitting)")
    s.set_defaults(fn=cmd_study)
    t = sub.add_parser("today", help="tag this weekend, estimate the gap, show matching history")
    t.add_argument("--mock", action="store_true")
    t.add_argument("--llm", action="store_true")
    t.add_argument("--gap", action="append", help="manual gap in %, e.g. --gap SPY=0.45 (repeatable)")
    t.add_argument("--seed", type=int, default=42)
    t.set_defaults(fn=cmd_today)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
