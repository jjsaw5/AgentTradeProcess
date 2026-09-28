"""Self-contained HTML reports: inline CSS, no external assets, light/dark via
prefers-color-scheme, tables that scroll horizontally on a phone."""
from __future__ import annotations

import html
from datetime import date

import numpy as np
import pandas as pd

from analyze import SIGNAL_METRICS, VIEWS

CSS = """
:root{--bg:#fbfbf9;--fg:#1c1c1a;--muted:#6b6b66;--line:#dcdcd6;--card:#ffffff;--acc:#1f5fa8;
--ok:#1d7a3e;--warn:#a86a00;--bad:#a83232;--okbg:#e6f4ea;--warnbg:#fff3df;--badbg:#fbe7e7;--thead:#f0efe9;}
@media (prefers-color-scheme: dark){:root{--bg:#141414;--fg:#e8e6e0;--muted:#9a978f;--line:#333;--card:#1d1d1d;
--acc:#7fb1ee;--ok:#7fd39a;--warn:#f0b452;--bad:#f08a8a;--okbg:#153d22;--warnbg:#3d2c10;--badbg:#3d1717;--thead:#242424;}}
*{box-sizing:border-box}body{margin:0;padding:16px;background:var(--bg);color:var(--fg);
font:15px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
h1{font-size:1.5rem;margin:.2rem 0 .3rem}h2{font-size:1.15rem;margin:1.6rem 0 .5rem;border-bottom:1px solid var(--line);padding-bottom:.2rem}
h3{font-size:1rem;margin:1.1rem 0 .4rem;color:var(--muted)}p{margin:.4rem 0}.muted{color:var(--muted)}
.scope{color:var(--muted);font-size:.9rem}.tiles{display:flex;flex-wrap:wrap;gap:12px;margin:.6rem 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:150px}
.tile .k{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.tile .v{font-size:1.4rem;font-weight:600}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:.4rem 0 1rem}
table{border-collapse:collapse;font-size:.85rem;white-space:nowrap;min-width:100%}
th,td{border:1px solid var(--line);padding:4px 8px;text-align:right}th{background:var(--thead);position:sticky;top:0}
td:first-child,th:first-child{text-align:left}td.l{text-align:left;white-space:normal;min-width:220px}
.confirmed{background:var(--okbg);color:var(--ok)}.failed{background:var(--badbg);color:var(--bad)}.disc{background:var(--warnbg);color:var(--warn)}
.note{background:var(--card);border-left:4px solid var(--acc);padding:8px 12px;margin:.6rem 0;border-radius:4px}
.caution{border-left-color:var(--warn)}ul{margin:.3rem 0 .3rem 1.2rem}code{font-size:.85em}
"""


def _e(x) -> str:
    return html.escape("" if x is None else str(x))


def pct(x, digits=0) -> str:
    return "—" if x is None or not np.isfinite(x) else f"{100 * x:.{digits}f}%"


def num(x, digits=2, sign=True) -> str:
    if x is None or not np.isfinite(x):
        return "—"
    return f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"


def _status_class(s: str) -> str:
    return {"confirmed": "confirmed", "failed holdout": "failed", "discovery only": "disc"}.get(s, "")


def _page(title: str, body: str) -> str:
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<meta name='color-scheme' content='light dark'><title>{_e(title)}</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")


GROUP_COLS = [
    ("n disc", lambda r: f"{int(r['n_disc'])}"),
    ("n hold", lambda r: f"{int(r['n_hold'])}"),
    ("avg |gap|", lambda r: num(r["mean_abs_gap_disc"], 2, sign=False)),
    ("fill same day", lambda r: pct(r["rate_fill_same_day_disc"])),
    ("fill 1st hr", lambda r: pct(r["rate_fill_1h_disc"])),
    ("median min to fill", lambda r: num(r["median_min_to_fill_disc"], 0, sign=False)),
    ("close with gap", lambda r: pct(r["rate_continuation_disc"])),
    ("0DTE %", lambda r: num(r["mean_h0_ret_disc"])),
    ("1DTE %", lambda r: num(r["mean_h1_ret_disc"])),
    ("4DTE %", lambda r: num(r["mean_h4_ret_disc"])),
    ("1st 30m holds", lambda r: pct(r["rate_first30_holds_disc"])),
]


def _group_table(rows: pd.DataFrame, ticker: str, view: str) -> str:
    head = "".join(f"<th>{_e(c)}</th>" for c in ["group"] + [c for c, _ in GROUP_COLS] + ["signals", "implication"])
    body = []
    for _, r in rows.iterrows():
        cells = [f"<td>{_e(r['group'])}</td>"] + [f"<td>{fn(r)}</td>" for _, fn in GROUP_COLS]
        cells.append(f"<td class='l {_status_class(r['status'])}'>{_e(r['signals'])}</td>")
        cells.append(f"<td class='l'>{_e(r['implication'])}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (f"<div class='scroll'><table class='grp' data-ticker='{_e(ticker)}' data-view='{_e(view)}'>"
            f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>")


def study_report(an, df: pd.DataFrame, notes: dict, cfg) -> str:
    tickers = list(cfg.tickers)
    d0, d1 = an.date_range
    parts = [f"<h1>Monday Edge — study report</h1>",
             f"<p class='scope'>{an.n_sessions} post-weekend sessions, {d0} → {d1}. "
             f"Discovery before {an.cut_date}, holdout from {an.cut_date} (newest {int(cfg.holdout_frac * 100)}%). "
             f"Tickers: {', '.join(tickers)}. Tagger: {_e(notes.get('tagger', 'rules'))}. Generated {date.today()}.</p>"]

    # KPI tiles
    tiles = []
    for t in tickers:
        k = an.kpis.get(t, {})
        tiles.append(f"<div class='tile'><div class='k'>{_e(t)} same-day fill</div><div class='v'>{pct(k.get('fill_same_day'))}</div>"
                     f"<div class='muted'>n={k.get('n', 0)}</div></div>")
        tiles.append(f"<div class='tile'><div class='k'>{_e(t)} close with gap</div><div class='v'>{pct(k.get('continuation'))}</div>"
                     f"<div class='muted'>baseline, all weekends</div></div>")
    parts.append(f"<div class='tiles'>{''.join(tiles)}</div>")

    # Confirmed patterns
    parts.append("<h2>Confirmed patterns</h2>")
    conf = an.confirmed
    if conf.empty:
        parts.append("<p class='note'>No pattern survived the holdout. That is a valid result: nothing here is a trade idea.</p>")
    else:
        rows = "".join(
            f"<tr><td>{_e(r['ticker'])}</td><td>{_e(r['view'])}</td><td>{_e(r['group'])}</td><td>{int(r['n_disc'])}/{int(r['n_hold'])}</td>"
            f"<td class='l confirmed'>{_e(r['signals'])}</td><td class='l'>{_e(r['implication'])}</td></tr>"
            for _, r in conf.iterrows())
        parts.append("<div class='scroll'><table id='confirmed'><thead><tr><th>ticker</th><th>view</th><th>group</th><th>n disc/hold</th>"
                     f"<th>pattern</th><th>implication</th></tr></thead><tbody>{rows}</tbody></table></div>")
    fluke = "; ".join(f"{t}: {an.n_tests.get(t, 0)} eligible tests → ≈{an.expected_flukes.get(t, 0):.1f} expected flukes"
                      for t in tickers)
    parts.append(f"<p class='note'><b>Fluke count.</b> Pure noise passes both tests about 0.7% of the time. {fluke}. "
                 f"{len(conf)} confirmed row(s) above. SPY and QQQ are highly correlated: a pattern in both is one finding, not two. "
                 f"Every pattern here is history, not a track record — the process is UNCALIBRATED until live Mondays are logged against it.</p>")

    # How to read
    parts.append("<h2>How to read the tables</h2><ul>"
                 "<li><b>Returns are underlying moves in %, not option P&amp;L.</b> Sign is relative to the gap: positive = continued with the gap.</li>"
                 "<li>Table values are the <b>discovery</b> split (the newest 30% of weekends is held out and only used to confirm). "
                 "<code>patterns.csv</code> carries discovery, holdout and all-data stats.</li>"
                 "<li><b>fill same day</b>: low (up gap) / high (down gap) reached Friday's close on Monday. <b>fill 1st hr</b>: within 60 minutes (bar end). "
                 "<b>median min to fill</b>: minutes from 09:30, filled sessions only.</li>"
                 "<li><b>close with gap</b>: Monday closed on the gap side of the open. <b>0/1/4DTE %</b>: mean signed move open→close at that horizon.</li>"
                 "<li><b>1st 30m holds</b>: the direction of the first 30 minutes matched the direction of the rest of the day.</li>"
                 "<li><b>signals</b>: z-scores against a <b>size-adjusted baseline</b> (each group vs what its own mix of flat/small/large gaps would give), "
                 "discovery z / holdout z. <span class='confirmed'>confirmed</span> = |z|≥2 in discovery and the holdout (n≥5) agrees with |z|≥1; "
                 "<span class='failed'>failed holdout</span> = discovery passed, holdout opposite or weak; "
                 "<span class='disc'>discovery only</span> = holdout too small to say. Groups with n disc &lt; "
                 f"{cfg.min_n} are never eligible.</li>"
                 "<li>Gap sizes: flat &lt; {gf}% ≤ small &lt; {gl}% ≤ large. EM = Friday's implied 1-day move (UW). "
                 "GEX / VIX / EM are Friday values — nothing from Monday leaks into context.</li></ul>".format(gf=cfg.gap_flat, gl=cfg.gap_large))

    # Tables per ticker per view
    for t in tickers:
        parts.append(f"<h2>{_e(t)}</h2>")
        pt = an.patterns[an.patterns["ticker"] == t]
        base = pt[pt["view"] == "ALL"]
        for view, _keys in VIEWS:
            rows = pd.concat([base, pt[pt["view"] == view]])
            parts.append(f"<h3>{_e(view)}</h3>")
            parts.append(_group_table(rows, t, view))

    # Recent weekends
    parts.append("<h2>Most recent 30 weekends</h2>")
    d2 = df.copy()
    d2["session"] = pd.to_datetime(d2["session"]).dt.date
    sessions = sorted(d2["session"].unique(), reverse=True)[:30]
    head = ["session", "category", "Trump", "tone"] + [f"{t} gap / filled / 0DTE" for t in tickers] + ["headlines or summary"]
    body = []
    for s in sessions:
        g = d2[d2["session"] == s]
        first = g.iloc[0]
        cells = [f"<td>{s}</td><td>{_e(first['category'])}</td><td>{_e(first['trump_mode'])}</td><td>{_e(first['risk_tone'])}</td>"]
        for t in tickers:
            r = g[g["ticker"] == t]
            if r.empty:
                cells.append("<td>—</td>")
                continue
            r = r.iloc[0]
            filled = "yes" if str(r["fill_same_day"]).lower() in ("true", "1", "1.0") else "no"
            cells.append(f"<td>{num(r['gap_pct'])}% / {filled} / {num(r['h0_ret'])}%</td>")
        text = first["summary"] if isinstance(first.get("summary"), str) and first["summary"] else first["top_headlines"]
        cells.append(f"<td class='l'>{_e(str(text)[:300] if isinstance(text, str) else '')}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    parts.append("<div class='scroll'><table id='recent'><thead><tr>" + "".join(f"<th>{_e(h)}</th>" for h in head) +
                 f"</tr></thead><tbody>{''.join(body)}</tbody></table></div>")

    # Data notes
    uw_notes = notes.get("uw_notes") or []
    fmp_notes = notes.get("fmp_notes") or []
    parts.append("<h2>Data notes</h2><ul>")
    parts.append(f"<li>Missing intraday bars: {notes.get('missing_intraday_pct', float('nan')):.1f}% of session×ticker rows "
                 "(daily fill still computed; intraday fields NaN).</li>")
    parts.append(f"<li>Weekends with no headlines in the window: {notes.get('no_headlines_pct', float('nan')):.1f}% (tagged quiet by construction).</li>")
    parts.append("<li>Unusual Whales: " + ("; ".join(_e(n) for n in uw_notes) if uw_notes else "no gaps reported") + "</li>")
    if fmp_notes:
        parts.append("<li>FMP: " + "; ".join(_e(n) for n in sorted(set(fmp_notes))[:10]) + "</li>")
    parts.append("<li><b>No look-ahead:</b> every context column (gap, Friday/prior-week return, VIX, GEX, implied move, news) uses only "
                 "Friday data and the Friday 16:00 ET → Monday 09:30 ET news window. Outcomes start at the Monday open.</li>")
    parts.append("<li>Rule-based tagging counts keywords; compare with <code>--llm</code> before trusting a category split.</li>")
    parts.append("<li>Early-close Fridays: the window still starts at 16:00, so 13:00–16:00 news on those days is lost.</li></ul>")
    return _page("Monday Edge — study", "".join(parts))


def _analog_table(rows: list[dict]) -> str:
    head = ["tier", "match", "n", "fill same day", "fill 1st hr", "median min to fill", "close with gap",
            "0DTE %", "1DTE %", "4DTE %", "0DTE MFE %", "0DTE MAE %"]
    body = []
    for r in rows:
        body.append("<tr>" + "".join([
            f"<td>{_e(r['tier'])}</td>", f"<td class='l'>{_e(r['match'])}</td>", f"<td>{r['n']}</td>",
            f"<td>{pct(r['rate_fill_same_day'])}</td>", f"<td>{pct(r['rate_fill_1h'])}</td>",
            f"<td>{num(r['median_min_to_fill'], 0, sign=False)}</td>", f"<td>{pct(r['rate_continuation'])}</td>",
            f"<td>{num(r['mean_h0_ret'])}</td>", f"<td>{num(r['mean_h1_ret'])}</td>", f"<td>{num(r['mean_h4_ret'])}</td>",
            f"<td>{num(r['mean_h0_mfe'], 2, sign=False)}</td>", f"<td>{num(r['mean_h0_mae'], 2, sign=False)}</td>"]) + "</tr>")
    return ("<div class='scroll'><table class='analog'><thead><tr>" + "".join(f"<th>{_e(h)}</th>" for h in head) +
            f"</tr></thead><tbody>{''.join(body)}</tbody></table></div>")


def today_brief(today: date, window: tuple, tag: dict, per_ticker: dict, analog_rows: dict, matches: dict,
                headlines: list[dict], is_session: bool, cfg) -> str:
    w0, w1 = window
    parts = [f"<h1>Monday Edge — brief for {today}</h1>",
             f"<p class='scope'>News window {w0.strftime('%Y-%m-%d %H:%M')} → {w1.strftime('%Y-%m-%d %H:%M')} UTC. "
             + ("" if is_session else "<b>Today does not follow a 3+ day break</b>; the analogs are post-weekend history and may not apply. ")
             + f"Tagger: {_e(tag.get('tagger'))}.</p>"]
    parts.append("<div class='tiles'>"
                 f"<div class='tile'><div class='k'>category</div><div class='v'>{_e(tag.get('category'))}</div>"
                 f"<div class='muted'>score {tag.get('category_score', 0):.0f}, 2nd: {_e(tag.get('category_2nd') or '—')}</div></div>"
                 f"<div class='tile'><div class='k'>risk tone</div><div class='v'>{_e(tag.get('risk_tone'))}</div><div class='muted'>net {tag.get('tone_score', 0):+d}</div></div>"
                 f"<div class='tile'><div class='k'>Trump mode</div><div class='v'>{_e(tag.get('trump_mode'))}</div>"
                 f"<div class='muted'>{tag.get('trump_market_posts', 0)} market posts</div></div>"
                 f"<div class='tile'><div class='k'>headlines</div><div class='v'>{tag.get('n_headlines', 0)}</div></div></div>")
    if tag.get("summary"):
        parts.append(f"<p class='note'><b>Model summary (interpretation, not fact):</b> {_e(tag['summary'])}</p>")

    for t, info in per_ticker.items():
        parts.append(f"<h2>{_e(t)}</h2>")
        parts.append("<div class='tiles'>"
                     f"<div class='tile'><div class='k'>gap</div><div class='v'>{num(info.get('gap_pct'))}%</div><div class='muted'>{_e(info.get('gap_source'))}</div></div>"
                     f"<div class='tile'><div class='k'>gap size</div><div class='v'>{_e(info.get('gap_size'))}</div><div class='muted'>{_e(info.get('gap_bucket'))} · {_e(info.get('em_bucket'))}</div></div>"
                     f"<div class='tile'><div class='k'>Friday close</div><div class='v'>{num(info.get('prev_close'), 2, sign=False)}</div><div class='muted'>{_e(info.get('prev'))}</div></div>"
                     f"<div class='tile'><div class='k'>implied 1-day move</div><div class='v'>{num(info.get('em1_pct'), 2, sign=False)}%</div><div class='muted'>UW, Friday</div></div>"
                     f"<div class='tile'><div class='k'>Friday GEX</div><div class='v'>{_e(info.get('gex_regime'))}</div>"
                     f"<div class='muted'>pctile {num(info.get('gex_pctile'), 0, sign=False)} · VIX {_e(info.get('vix_regime'))}</div></div></div>")
        parts.append("<h3>Analogs (all history, narrowest → broadest)</h3>")
        rows = analog_rows.get(t) or []
        parts.append(_analog_table(rows) if rows else "<p class='muted'>No matching history.</p>")
        m = matches.get(t)
        parts.append("<h3>Confirmed patterns that match this weekend</h3>")
        if m is None or m.empty:
            parts.append("<p class='muted'>None. No confirmed pattern's group matches today's attributes.</p>")
        else:
            body = "".join(f"<tr><td>{_e(r['view'])}</td><td>{_e(r['group'])}</td><td>{int(r['n_disc'])}/{int(r['n_hold'])}</td>"
                           f"<td class='l confirmed'>{_e(r['signals'])}</td><td class='l'>{_e(r['implication'])}</td></tr>"
                           for _, r in m.iterrows())
            parts.append("<div class='scroll'><table class='matches'><thead><tr><th>view</th><th>group</th><th>n disc/hold</th><th>pattern</th>"
                         f"<th>implication</th></tr></thead><tbody>{body}</tbody></table></div>")

    parts.append("<h2>Top headlines</h2><ul>")
    for h in headlines[:15]:
        flag = " <b>[major]</b>" if h.get("is_major") else ""
        parts.append(f"<li>{_e(h.get('published_utc', '')[:16])} — {_e(h.get('title'))}{flag}</li>")
    if not headlines:
        parts.append("<li class='muted'>No headlines in the window (from the sources reached). Tagged quiet by construction.</li>")
    parts.append("</ul>")
    parts.append("<p class='note caution'><b>Caution.</b> Rows with n under ~15 are anecdotes, not evidence. On a fill thesis, wait out the first 30 minutes. "
                 "Size by the Playbook gates; returns above are underlying moves, not option P&amp;L. This tool frames a decision — the human executes every order.</p>")
    return _page(f"Monday Edge — {today}", "".join(parts))
