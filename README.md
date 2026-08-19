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
