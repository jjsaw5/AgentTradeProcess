"""Group statistics, size-adjusted baseline, and the discovery/holdout test.

Why the size adjustment (spec §8.4): fill rates and with-gap returns depend
heavily on gap size, so a raw average makes groups of small gaps look special.
Each group is compared against what its own gap-size mix would produce.

Why these thresholds (spec §8.6): a noise group passes |z_disc| >= 2 about
4.6% of the time, and then a same-direction |z_hold| >= 1 about 15.9% of the
time, so pure noise is "confirmed" roughly 0.7% of the time per test. The
report shows the number of eligible tests and the implied fluke count.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

SIGNAL_METRICS = {"fill_same_day": "rate", "continuation": "rate", "h0_ret": "mean", "h4_ret": "mean"}
RATE_METRICS = ("fill_same_day", "fill_1h", "continuation", "first30_holds", "orb_follow", "h1_fill", "h4_fill")
MEAN_METRICS = ("h0_ret", "h1_ret", "h2_ret", "h4_ret", "h0_mfe", "h0_mae")
VIEWS = [
    ("category", ["category"]),
    ("gap_bucket", ["gap_bucket"]),
    ("em_bucket", ["em_bucket"]),
    ("trump_mode", ["trump_mode"]),
    ("tone_vs_gap", ["tone_vs_gap"]),
    ("gex_regime", ["gex_regime"]),
    ("vix_regime", ["vix_regime"]),
    ("prior_week_dir_vs_gap", ["prior_week_dir_vs_gap"]),
    ("category x gap_size", ["category", "gap_size"]),
    ("trump_mode x gap_size", ["trump_mode", "gap_size"]),
    ("gex_regime x gap_size", ["gex_regime", "gap_size"]),
]
FLUKE_RATE = 0.007
METRIC_LABEL = {"fill_same_day": "fill", "continuation": "cont", "h0_ret": "0DTE", "h4_ret": "4DTE"}
IMPLICATION = {
    ("fill_same_day", 1): "fade toward Friday close (0DTE)",
    ("fill_same_day", -1): "gap tends to hold — no fade (0DTE)",
    ("continuation", 1): "trade with the gap (0DTE)",
    ("continuation", -1): "gap reverses intraday (0DTE fade)",
    ("h0_ret", 1): "trade with the gap (0DTE)",
    ("h0_ret", -1): "gap reverses intraday (0DTE fade)",
    ("h4_ret", 1): "with the gap into Friday (2-4DTE)",
    ("h4_ret", -1): "against the gap into Friday (2-4DTE)",
}


def split_sessions(df: pd.DataFrame, holdout_frac: float) -> tuple[pd.DataFrame, date]:
    """Sort unique session dates; everything before the (1-holdout_frac) quantile date is discovery."""
    dates = sorted(pd.to_datetime(df["session"]).dt.date.unique())
    if not dates:
        raise ValueError("no sessions")
    cut_idx = int(np.floor(len(dates) * (1.0 - holdout_frac)))
    cut_idx = min(max(cut_idx, 1), len(dates) - 1) if len(dates) > 1 else 0
    cut = dates[cut_idx]
    out = df.copy()
    out["session"] = pd.to_datetime(out["session"]).dt.date
    out["split"] = np.where(out["session"] < cut, "discovery", "holdout")
    return out, cut


def _bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.astype(float)
    return s.map(lambda v: np.nan if (v is None or (isinstance(v, float) and np.isnan(v)))
                 else float(str(v).strip().lower() in ("true", "1", "1.0")))


def group_stats(g: pd.DataFrame) -> dict:
    out = {"n": int(len(g))}
    for m in RATE_METRICS:
        s = _bool_series(g[m]) if m in g else pd.Series(dtype=float)
        out[f"rate_{m}"] = float(s.mean()) if s.notna().any() else np.nan
        out[f"n_{m}"] = int(s.notna().sum())
    for m in MEAN_METRICS:
        s = pd.to_numeric(g[m], errors="coerce") if m in g else pd.Series(dtype=float)
        out[f"mean_{m}"] = float(s.mean()) if s.notna().any() else np.nan
        out[f"sd_{m}"] = float(s.std(ddof=1)) if s.notna().sum() > 1 else np.nan
        out[f"n_{m}"] = int(s.notna().sum())
    mtf = pd.to_numeric(g["min_to_fill"], errors="coerce") if "min_to_fill" in g else pd.Series(dtype=float)
    out["median_min_to_fill"] = float(mtf.median()) if mtf.notna().any() else np.nan
    out["mean_abs_gap"] = float(pd.to_numeric(g["gap_pct"], errors="coerce").abs().mean()) if len(g) else np.nan
    return out


def size_baseline(sub: pd.DataFrame) -> dict:
    """{gap_size: {metric: mean}} over all weekends in one split (one ticker)."""
    base = {}
    for size, g in sub.groupby("gap_size"):
        d = {}
        for m, kind in SIGNAL_METRICS.items():
            s = _bool_series(g[m]) if kind == "rate" else pd.to_numeric(g[m], errors="coerce")
            d[m] = float(s.mean()) if s.notna().any() else np.nan
        base[size] = d
    return base


def expected_for(g: pd.DataFrame, base: dict) -> dict:
    """Size-adjusted expectation: sum over sizes of share_in_size x baseline_mean(size)."""
    shares = g["gap_size"].value_counts(normalize=True)
    out = {}
    for m in SIGNAL_METRICS:
        tot, wsum = 0.0, 0.0
        for size, share in shares.items():
            b = base.get(size, {}).get(m, np.nan)
            if np.isfinite(b):
                tot += share * b
                wsum += share
        out[m] = tot / wsum if wsum > 0 else np.nan
    return out


def zscore(kind: str, value: float, expected: float, sd: float, n: int) -> float:
    if n <= 0 or not (np.isfinite(value) and np.isfinite(expected)):
        return np.nan
    if kind == "rate":
        p0 = min(max(expected, 0.01), 0.99)  # avoid a zero denominator on a degenerate baseline
        return (value - p0) / np.sqrt(p0 * (1 - p0) / n)
    if not np.isfinite(sd) or sd <= 0 or n < 2:
        return np.nan
    return (value - expected) / (sd / np.sqrt(n))


def _status(n_disc, z_disc, n_hold, z_hold, min_n: int) -> str:
    if n_disc < min_n or not np.isfinite(z_disc) or abs(z_disc) < 2.0:
        return ""
    if n_hold < 5:
        return "discovery only"
    if np.isfinite(z_hold) and np.sign(z_hold) == np.sign(z_disc) and abs(z_hold) >= 1.0:
        return "confirmed"
    return "failed holdout"


@dataclass
class Analysis:
    patterns: pd.DataFrame
    cut_date: date
    n_sessions: int
    date_range: tuple
    baselines: dict = field(default_factory=dict)   # ticker -> {"discovery": {...}, "holdout": {...}}
    n_tests: dict = field(default_factory=dict)      # ticker -> eligible tests
    expected_flukes: dict = field(default_factory=dict)
    kpis: dict = field(default_factory=dict)         # ticker -> {fill_same_day, continuation}

    @property
    def confirmed(self) -> pd.DataFrame:
        return self.patterns[self.patterns["status"] == "confirmed"].copy()


def _label(keys: list[str], vals) -> str:
    vals = vals if isinstance(vals, tuple) else (vals,)
    return " | ".join(str(v) for v in vals)


def analyze(df: pd.DataFrame, cfg) -> Analysis:
    data, cut = split_sessions(df, cfg.holdout_frac)
    rows = []
    baselines, n_tests, flukes, kpis = {}, {}, {}, {}
    for ticker, td in data.groupby("ticker"):
        disc = td[td["split"] == "discovery"]
        hold = td[td["split"] == "holdout"]
        base = {"discovery": size_baseline(disc), "holdout": size_baseline(hold)}
        baselines[ticker] = base
        kpis[ticker] = {"fill_same_day": _bool_series(td["fill_same_day"]).mean(),
                        "continuation": _bool_series(td["continuation"]).mean(), "n": len(td)}
        eligible = 0

        def make_row(view, keys, label, gd, gh, gall):
            r = {"ticker": ticker, "view": view, "group": label}
            for k in (keys or []):
                r[f"key_{k}"] = gd[k].iloc[0] if len(gd) else (gh[k].iloc[0] if len(gh) else "")
            sd_, sh_, sa_ = group_stats(gd), group_stats(gh), group_stats(gall)
            r["n_disc"], r["n_hold"], r["n_all"] = sd_["n"], sh_["n"], sa_["n"]
            for k, v in sd_.items():
                if k != "n":
                    r[f"{k}_disc"] = v
            for k, v in sh_.items():
                if k != "n":
                    r[f"{k}_hold"] = v
            for k, v in sa_.items():
                if k != "n":
                    r[f"{k}_all"] = v
            ed = expected_for(gd, base["discovery"]) if len(gd) else {}
            eh = expected_for(gh, base["holdout"]) if len(gh) else {}
            sigs, imps, statuses = [], [], []
            for m, kind in SIGNAL_METRICS.items():
                vd = sd_[f"rate_{m}"] if kind == "rate" else sd_[f"mean_{m}"]
                vh = sh_[f"rate_{m}"] if kind == "rate" else sh_[f"mean_{m}"]
                nd = sd_[f"n_{m}"]
                nh = sh_[f"n_{m}"]
                zd = zscore(kind, vd, ed.get(m, np.nan), sd_.get(f"sd_{m}", np.nan), nd)
                zh = zscore(kind, vh, eh.get(m, np.nan), sh_.get(f"sd_{m}", np.nan), nh)
                st = _status(nd, zd, nh, zh, cfg.min_n) if label != "ALL WEEKENDS" else ""
                r[f"exp_{m}_disc"], r[f"exp_{m}_hold"] = ed.get(m, np.nan), eh.get(m, np.nan)
                r[f"z_{m}"], r[f"z_{m}_hold"], r[f"sig_{m}"] = zd, zh, st
                if st:
                    arrow = "↑" if zd > 0 else "↓"
                    sigs.append(f"{METRIC_LABEL[m]} {arrow} {st} (z {zd:+.1f}/{zh:+.1f})")
                    statuses.append(st)
                    if st == "confirmed":
                        imp = IMPLICATION[(m, 1 if zd > 0 else -1)]
                        if imp not in imps:
                            imps.append(imp)
            order = {"confirmed": 3, "failed holdout": 2, "discovery only": 1, "": 0}
            r["status"] = max(statuses, key=lambda s: order[s]) if statuses else ""
            r["signals"] = "; ".join(sigs)
            r["implication"] = "; ".join(imps)
            return r

        rows.append(make_row("ALL", [], "ALL WEEKENDS", disc, hold, td))
        for view, keys in VIEWS:
            for vals, gall in td.groupby(keys, sort=True):
                gd = gall[gall["split"] == "discovery"]
                gh = gall[gall["split"] == "holdout"]
                if len(gd) >= cfg.min_n:
                    eligible += len(SIGNAL_METRICS)
                rows.append(make_row(view, keys, _label(keys, vals), gd, gh, gall))
        n_tests[ticker] = eligible
        flukes[ticker] = eligible * FLUKE_RATE

    patterns = pd.DataFrame(rows)
    dates = sorted(data["session"].unique())
    return Analysis(patterns=patterns, cut_date=cut, n_sessions=len(dates), date_range=(dates[0], dates[-1]),
                    baselines=baselines, n_tests=n_tests, expected_flukes=flukes, kpis=kpis)


# ----- analogs (for `today`) -----

ANALOG_TIERS = [
    ("category + gap size + Trump mode", ["category", "gap_size", "trump_mode"]),
    ("category + gap size", ["category", "gap_size"]),
    ("category", ["category"]),
    ("gap size", ["gap_size"]),
    ("all weekends", []),
]


def analogs(df: pd.DataFrame, ticker: str, attrs: dict) -> list[dict]:
    """Stats for matching history, narrowest to broadest; empty tiers skipped."""
    td = df[df["ticker"] == ticker]
    out = []
    for label, keys in ANALOG_TIERS:
        g = td
        desc = []
        for k in keys:
            v = attrs.get(k)
            if v is None or v == "n/a":
                g = g.iloc[0:0]
                break
            g = g[g[k] == v]
            desc.append(f"{k}={v}")
        if len(g) == 0:
            continue
        st = group_stats(g)
        out.append({"tier": label, "match": ", ".join(desc) or "—", **st})
    return out


def matching_confirmed(an: Analysis, ticker: str, attrs: dict) -> pd.DataFrame:
    """Confirmed rows for `ticker` whose group keys all equal today's attributes."""
    c = an.confirmed
    c = c[c["ticker"] == ticker]
    keep = []
    for _, r in c.iterrows():
        keys = [col for col in r.index if col.startswith("key_") and pd.notna(r[col]) and r[col] != ""]
        ok = bool(keys)
        for col in keys:
            if attrs.get(col[4:]) != r[col]:
                ok = False
                break
        keep.append(ok)
    return c[keep] if len(c) else c
