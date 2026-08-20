#!/usr/bin/env bash
# Execute SQL against the briefscoring Turso database.
#
# Usage:
#   scoredb.sh "SELECT ..."             # single statement
#   scoredb.sh -f file.sql              # statements separated by lines of ';;'
#
# Credentials come from the environment or a gitignored .env next to the repo
# root: TURSO_URL (https://briefscoring-jjsaw5.aws-us-east-2.turso.io) and
# TURSO_TOKEN. Never hardcode either here (CLAUDE.md §6).
#
# Handy queries:
#   Cumulative:  SELECT SUM(radar_conf_paid)||'/'||SUM(radar_conf_fired),
#                SUM(wl_precision_hits)||'/'||SUM(wl_precision_total),
#                SUM(wl_recall_caught)||'/'||SUM(wl_recall_total)
#                FROM brief_reviews WHERE status='GRADED';
#   Open items:  SELECT * FROM open_items WHERE resolution IS NULL;
#   Ledger:      SELECT id,status,change FROM improvements ORDER BY id;

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -z "${TURSO_URL:-}" || -z "${TURSO_TOKEN:-}" ]]; then
  if [[ -f "$REPO_ROOT/.env" ]]; then
    # shellcheck disable=SC1091
    set -a; source "$REPO_ROOT/.env"; set +a
  fi
fi
if [[ -z "${TURSO_URL:-}" || -z "${TURSO_TOKEN:-}" ]]; then
  echo "TURSO_URL / TURSO_TOKEN not set (env or gitignored .env)" >&2
  exit 1
fi

if [[ "${1:-}" == "-f" ]]; then
  SQL_INPUT="$(cat "$2")"
else
  SQL_INPUT="${1:?usage: scoredb.sh \"SQL\" | scoredb.sh -f file.sql}"
fi

python3 - "$SQL_INPUT" <<'PYEOF'
import json, os, subprocess, sys
stmts = [s.strip() for s in sys.argv[1].split("\n;;\n") if s.strip()]
reqs = [{"type": "execute", "stmt": {"sql": s}} for s in stmts]
reqs.append({"type": "close"})
p = subprocess.run(
    ["curl", "-sS", "--fail-with-body", "-m", "60", "--retry", "3",
     "--retry-delay", "2", "--retry-all-errors",
     "-X", "POST", os.environ["TURSO_URL"] + "/v2/pipeline",
     "-H", "Authorization: Bearer " + os.environ["TURSO_TOKEN"],
     "-H", "Content-Type: application/json", "--data-binary", "@-"],
    input=json.dumps({"requests": reqs}).encode(), capture_output=True)
if p.returncode != 0:
    sys.stderr.write("FETCH FAILED: " + p.stderr.decode() + "\n"); sys.exit(1)
out = json.loads(p.stdout)
ok = True
for r in out["results"][:-1]:
    if r["type"] == "error":
        ok = False
        print("ERROR:", json.dumps(r["error"]))
        continue
    res = r["response"]["result"]
    if res["cols"]:
        print(" | ".join(c["name"] for c in res["cols"]))
        for row in res["rows"]:
            print(" | ".join(c.get("value", "NULL") for c in row))
    else:
        print(f"ok ({res['affected_row_count']} rows affected)")
sys.exit(0 if ok else 1)
PYEOF
