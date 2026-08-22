# AgentTradeProcess

The versioned home of my agent-assisted trading process. Specs live here;
runtime copies (scheduled tasks, skills) load from or sync to this repo.

## Contents

- `daily-market-brief/SKILL.md` — the full spec for the daily 9:05 AM ET
  pre-market intelligence brief: data sources (Robinhood MCP, Unusual Whales,
  FMP), the hardened-curl rule, section-by-section format (§0 setup ritual
  through §13 known-unknowns), the §8A UW discovery scan, squeeze radar
  methodology, gamma-regime reporting, and honesty rules (UNVERIFIED labels,
  absent-stays-absent, no invented drivers).

## Conventions

- The brief runs as a Claude Code scheduled task (`daily-market-breif`,
  weekdays 9:05 AM ET) whose runtime SKILL.md defers to this repo's copy.
  Edit HERE, not the runtime copy.
- API keys live in the trading-bot repo's `.env` (gitignored there) — never
  in this repo. The spec references them by variable name only.
- Changes to the spec are commits — the process has a history, like the
  governance lesson that birthed it: a rule with no durable home is not a rule.

- `playbook/PLAYBOOK.md` — the discretionary trading playbook: philosophy,
  the 20-minute pre-market ritual, the four-step trade hierarchy
  (environment → location → confirmation → execution), event protocol,
  dated validated market behaviors, monitoring infrastructure, session
  grading, and the trading journal. Journal entries append HERE now.

- `briefs/YYYY-MM-DD.md` — the archived output of each day's brief run
  (added 2026-08-18). Each scheduled run writes its full brief here, commits,
  and pushes (see the spec's OUTPUT DELIVERY section). One file per trading
  day; automated runs touch only this directory.

- `uw-earnings-vol-scan/SKILL.md` — a **third-party** skill (Unusual Whales /
  Volatility Vibes), vendored verbatim on 2026-08-22: scans the earnings
  calendar for IV-crush setups and scores each name Recommended / Consider /
  Avoid for a long call calendar spread. `uw-earnings-vol-scan/README.md` is
  ours and records the provenance, the import-time verification (the skill's
  own selftest, 124/124), and how it sits under `CLAUDE.md` — its verdicts are
  `UNCALIBRATED` here, and this repo's §5 risk limits override its sizing prose.
  `.claude/skills/uw-earnings-vol-scan` symlinks to it so sessions started from
  this repo load it. Edit the vendored SKILL.md only to re-import upstream.
