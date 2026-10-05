# Vendored third-party skills

Claude Code auto-loads every skill in this directory for sessions started in
this repository. A skill is standing instruction, so each one here was read in
full before it was committed, and is pinned to an exact upstream commit. It is
**not** installed through a plugin marketplace with auto-update, because an
upstream push would then change this repo's instructions without leaving a
trace in this repo's history (CLAUDE.md §0).

**Do not edit the vendored bodies.** To update, re-copy from upstream at a new
commit, re-read the diff, and update the row below. Local corrections go in this
file, not in the copy.

| Skill | Upstream | Commit | Fetched | License |
|---|---|---|---|---|
| `diagram-design/` | https://github.com/cathrynlavery/diagram-design (`skills/diagram-design/`) | `cb80b0d299a5c0674e0d133d33f91f19af8cda0f` (plugin v2.6.56) | 2026-10-05 | MIT (`diagram-design/LICENSE`; bundled icon licenses in `THIRD_PARTY_LICENSES.md`) |

## diagram-design — scope and review notes

- **What it does:** writes self-contained HTML + inline SVG diagrams
  (architecture, flowchart, sequence, state machine, timeline, swimlane, etc.)
  in an editorial style. It produces pictures; it has no bearing on trading,
  data, or any honesty rule in CLAUDE.md §3. Where its guidance and this repo's
  governance disagree, CLAUDE.md wins.
- **Network:** none from the skill's scripts. Generated HTML loads Google Fonts
  when opened in a browser. Brand onboarding from a website URL fetches that
  site only if asked.
- **Scripts reviewed** (`scripts/*.py`): standard library only, no subprocess,
  no network, no file writes outside the paths passed in. `self_check.py`
  validates a generated diagram: `python3 .claude/skills/diagram-design/scripts/self_check.py <file>`.
- **Not vendored:** the upstream repo's slash commands (`/doctor`,
  `/export-diagram`, `/import-*`, `/profile`), CI scripts, and plugin
  manifests. The skill body covers import and export directly.
- **Style-guide gate:** on its first diagram the skill asks whether to
  customise `references/style-guide.md` (brand colours and fonts). The shipped
  default is in force until the owner chooses otherwise; a customised palette
  would be a local edit and should be recorded here.
- **Where diagrams go:** the skill does not choose. Diagrams that document a
  spec belong next to that spec (e.g. `day-plan/diagrams/`); throwaway ones do
  not get committed.
