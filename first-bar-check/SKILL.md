# FIRST-BAR CHECK — the 9:46 and 10:16 confirmation

**Ratified 2026-10-01 by the account owner (ledger D-4).** Status:
UNCALIBRATED (`CLAUDE.md` §7) until `brief-review` has graded 20 checks.

The morning brief is built from yesterday's close and the premarket. Its
gamma read (ceilings, floors, switch line) cannot see today's 0DTE
positioning, and its open read is based on prices from ~9:08 that drift
before the bell. This check answers one question, after the first bar that
the owner's own rules allow to count (I-14: the 9:30 candle never confirms):

> **Is the brief's DAY TYPE still true — STUCK, RUNNING or UNCLEAR — and what
> is now on or off the table?**

It is **not** a second brief. It re-derives nothing the open cannot change
(earnings, FDA, squeeze data, overnight flow). It must finish fast: fire at
**9:46 ET**, deliver by **~9:52**. On days the brief's §3 lists a scheduled
release at 10:00, run again at **10:16** (candles two and three, the S5 event
gate) with the same steps.

Claude never places, modifies or cancels an order (`CLAUDE.md` §2). The check
reports; the owner decides.

---

## Inputs

1. **Today's brief** `briefs/YYYY-MM-DD.md` (git pull first). Read: the §0 DAY
   TYPE box, the LINES table, the §3 event times, the §9 radar go/wrong
   signals. If the file is missing, say so on line 1 and grade against
   yesterday's high/low only.
2. **Today's day-plan card** `day-plan/cards/YYYY-MM-DD.md` if it exists —
   its go/wrong signals are checked too.
3. **Robinhood (read-only MCP):** `get_equity_historicals` 5-minute bars,
   9:30 → now, for SPY, QQQ and every §9 / card ticker (≤10 per call).
   Aggregate to the 9:30–9:45 (and at 10:16, 10:00–10:15) 15-minute bar.
4. **Unusual Whales** — run `first-bar-check/tools/uw_snapshot.py` (one call,
   ~10 requests, prints a compact JSON summary; never prints the key). It
   pulls, for SPY and QQQ:
   - `gex-levels` — vendor call wall / put wall / magnet / flip, **timestamp
     asserted to today**; a stale timestamp is reported as stale, never used
     as live.
   - `spot-exposures/strike?limit=500` — live gamma by strike including
     today's volume; the window must bracket spot (DATA_LAYER §3e) or it is
     discarded.
   - `interpolated-iv` — the 1-day `implied_move_perc`: today's expected
     range in plain numbers.
   - `market-tide` — net call vs put premium, 5-minute bars since 9:30.
   - `net-prem-ticks` — per-minute net premium and net delta for SPY/QQQ.
   - `news/headlines` — rows since 9:30 that name a tracked ticker or carry a
     macro keyword (Fed, yields, jobs, oil, Iran, tariffs…). **`is_major` is
     ignored:** on 2026-10-01 the vendor set it on nearly every press release.
     To add the day's §9 / card tickers, set `FBC_TICKERS=TICK1,TICK2` when
     running the tool.
   Any request that fails, returns `data: []`, or carries a stale timestamp is
   reported as `UNVERIFIED — <endpoint>` on its line. Absent is never zero.

## The day-type decision (plain words, same table as the brief)

Take the first eligible 15-minute close (9:45; 10:15 on the second run):

- **RUNNING confirmed / changed to RUNNING** — SPY or QQQ closed outside
  yesterday's range or through the switch line, AND live gamma at that price
  is negative (or the vendor flip is now on the far side), AND tide leans the
  same way. Two of three is "leaning RUNNING", not RUNNING.
- **STUCK confirmed / changed to STUCK** — both closed inside yesterday's
  range and on the positive-gamma side of the switch line, or price sits on
  the expiration-day magnet.
- **UNCLEAR** — anything else. Say what single 15-minute close would settle
  it.

If the brief's box and this check disagree, **this check wins for today**,
and it says so in plain words on line 1 ("The brief said STUCK. The first bar
says RUNNING.").

## Output — eight lines maximum, plain words only

```
FIRST-BAR CHECK 9:46 — DAY TYPE: <STUCK / RUNNING / UNCLEAR> (<confirmed | changed from X>)
Why: <one sentence: where SPY and QQQ closed the 9:45 bar vs yesterday's high/low and the switch line>
Expected range today: SPY <a>–<b>, QQQ <c>–<d> (options market, ±x%) — <how much of it is already used>
Live levels: SPY ceiling <x> / floor <y> / switch <z> · QQQ … (<UW time>)
Options flow since 9:30: <calls or puts leading, and whether it agrees with price>
Fired: <each §9 / card go or wrong signal that fired on this close, with the price> — or "nothing fired"
Off the table: <cards killed, triggers voided by a gap, or "nothing">
Your rule for this day type: <the fixed rule text from the brief's §0, verbatim>
```

Add one more line only if the tool's `market_headlines` shows a relevant headline since
9:30 — the headline, its time, and "price reaction: <x>". Never explain a
move with a headline the timestamps don't support.

## Delivery and record

1. **Chat** — the eight lines are the final message of the run.
2. **Repo** — append the same block, under a `## FIRST-BAR CHECK HH:MM`
   heading, to `day-plan/cards/YYYY-MM-DD.md` (create the file with a
   one-line header if no card was written today). The card file is
   append-only after the open; the check never edits a card above it.
   Commit and push to the working branch and `main` (standing scope:
   `day-plan/cards/**`). Secret-scan the diff first. Delivery failure never
   blocks the chat message.
3. **Holiday / closed market** — one quiet line, no file, stop.

## Grading

`brief-review` grades each check the same evening: was the stated day type
the day's realized behaviour from that point to 3:00? Did any "Fired" line
misreport a close? Results go to the review file under `## First-bar check`
and to the DAY-TYPE RECORD. Twenty graded checks is the calibration bar.

## What this check refuses to do

- Recommend an entry, a size or a contract. It states what fired; the day
  card and the playbook decide what that means.
- Override the owner's rule. On a STUCK day the rule line is printed every
  time, including after a go signal fires.
- Run long. If a data source has not answered by 9:51, ship the lines with
  that source marked `UNVERIFIED` rather than wait.
