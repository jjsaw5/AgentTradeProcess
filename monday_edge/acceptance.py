#!/usr/bin/env python3
"""Acceptance test (spec §11). Pre-registered expectations, recorded before running:

  1. category=geopolitical is CONFIRMED for SPY and QQQ in >= 4 of 5 seeds.
  2. Confirmed rows not attributable to the planted geopolitical effect
     (group label does not contain "geopolitical") average <= 2 per seed.
  3. The Trump-action group shows continuation above its size-adjusted
     expectation, but is NOT confirmed because n_disc < min_n (the guard).
  4. `today --mock` and `today --mock --gap SPY=-0.3` both run and write the brief.
  5. Both HTML files parse cleanly; the study report has one table per
     grouping per ticker.

    python acceptance.py
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

import numpy as np

from analyze import VIEWS, analyze
from build import build_dataset
from config import settings
from mock_data import MockWorld
import run as cli

SEEDS = (7, 11, 23, 42, 99)


class _Check(HTMLParser):
    """Balanced-tag check for the structural tags; counts grouping tables per ticker."""
    BAL = ("html", "head", "body", "table", "thead", "tbody", "tr", "td", "th", "div", "ul", "li", "h1", "h2", "h3", "p")

    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.grp = [], [], {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and "grp" in (a.get("class") or "").split():
            self.grp.setdefault(a.get("data-ticker"), set()).add(a.get("data-view"))
        if tag in self.BAL:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.BAL:
            if not self.stack or self.stack[-1] != tag:
                self.errors.append(f"unbalanced </{tag}> at line {self.getpos()[0]}")
            else:
                self.stack.pop()


def parse_html(path: Path) -> _Check:
    c = _Check()
    c.feed(path.read_text(encoding="utf-8"))
    c.close()
    if c.stack:
        c.errors.append(f"unclosed tags: {c.stack}")
    return c


def main() -> int:
    results = []
    other_counts = []
    geo_ok = 0
    guard_ok = True
    for seed in SEEDS:
        world = MockWorld(seed=seed)
        cfg = settings(start=str(world.start))
        cfg.out_dir = cfg.out_dir / "mock" / f"acceptance_seed{seed}"
        cfg.cache_dir = cfg.cache_dir / "mock"
        cfg.ensure_dirs()
        fmp, uw = world.clients()
        df, _notes = build_dataset(fmp, uw, cfg, log=lambda s: None)
        an = analyze(df, cfg)
        conf = an.confirmed
        geo = conf[(conf["view"] == "category") & (conf["group"] == "geopolitical")]
        geo_both = set(geo["ticker"]) >= set(cfg.tickers)
        geo_ok += int(geo_both)
        other = conf[~conf["group"].str.contains("geopolitical")]
        other_counts.append(len(other))
        act = an.patterns[(an.patterns["view"] == "trump_mode") & (an.patterns["group"] == "action")]
        above = bool(len(act)) and bool((act["rate_continuation_disc"] > act["exp_continuation_disc"]).all())
        small = bool(len(act)) and bool((act["n_disc"] < cfg.min_n).all())
        not_conf = bool((act["status"] != "confirmed").all()) if len(act) else True
        guard_ok = guard_ok and above and small and not_conf
        results.append((seed, geo_both, len(other), int(act["n_disc"].max()) if len(act) else 0,
                        float(act["rate_continuation_disc"].mean()) if len(act) else np.nan,
                        float(act["exp_continuation_disc"].mean()) if len(act) else np.nan, above and small and not_conf))

    print(f"{'seed':>4} {'geo confirmed both':>18} {'other confirmed':>15} {'action n_disc':>13} {'action cont':>11} {'expected':>8} {'guard':>5}")
    for seed, gb, oc, nd, cont, exp, g in results:
        print(f"{seed:4d} {str(gb):>18} {oc:15d} {nd:13d} {cont:11.2f} {exp:8.2f} {str(g):>5}")

    # criterion 4: today --mock, with and without --gap
    rc_a = cli.main(["study", "--mock", "--seed", "42"])
    rc_b = cli.main(["today", "--mock", "--seed", "42"])
    rc_c = cli.main(["today", "--mock", "--seed", "42", "--gap", "SPY=-0.3"])
    cfg = settings()
    out = cfg.out_dir / "mock"
    briefs = sorted(out.glob("brief_*.html"))
    study = out / "study_report.html"
    today_ok = rc_a == 0 and rc_b == 0 and rc_c == 0 and bool(briefs) and study.is_file()

    # criterion 5: parse and count tables
    sp = parse_html(study)
    bp = parse_html(briefs[-1]) if briefs else None
    tables_ok = all(sp.grp.get(t, set()) == {v for v, _ in VIEWS} for t in cfg.tickers)
    html_ok = not sp.errors and bp is not None and not bp.errors and tables_ok
    grp_detail = {k: len(v) for k, v in sp.grp.items()}

    avg_other = sum(other_counts) / len(other_counts)
    checks = [
        ("1. geopolitical confirmed for SPY and QQQ in >= 4/5 seeds", geo_ok >= 4, f"{geo_ok}/5"),
        ("2. other confirmed rows average <= 2 per seed", avg_other <= 2, f"avg {avg_other:.1f} {other_counts}"),
        ("3. Trump-action above baseline but not confirmed (n_disc < min_n)", guard_ok, ""),
        ("4. today --mock and --gap SPY=-0.3 run and write the brief", today_ok, str(briefs[-1]) if briefs else "no brief"),
        ("5. HTML parses; one grouping table per view per ticker", html_ok,
         f"study errors={sp.errors[:2]} grouping tables per ticker={grp_detail} brief errors={(bp.errors[:2] if bp else 'n/a')}"),
    ]
    print()
    ok = True
    for name, passed, detail in checks:
        ok = ok and passed
        print(f"[{'PASS' if passed else 'FAIL'}] {name}  {detail}")
    print("\nACCEPTANCE", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
