#!/usr/bin/env bash
# Generate the bundled nursing fallback asset from the backend seed bank.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$ROOT/output/nursing_staff_nurse_output.json"
TARGET="$ROOT/mathwise_build/assets/nursing/nursing_seed_questions.json"

if [[ ! -f "$SOURCE" ]]; then
  echo "Error: source seed bank not found: $SOURCE"
  exit 1
fi

mkdir -p "$(dirname "$TARGET")"

# Extract only the questions array and write compact JSON.
python3 - <<PY "$SOURCE" "$TARGET"
import json, sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data.get("questions", [])
with open(sys.argv[2], "w", encoding="utf-8") as f:
    json.dump(questions, f, separators=(",", ":"), ensure_ascii=False)

print(f"Generated {sys.argv[2]} with {len(questions)} questions")
PY

SIZE_BYTES=$(stat -c%s "$TARGET")
SIZE_KB=$(( SIZE_BYTES / 1024 ))
echo "File size: ${SIZE_KB} KB (${SIZE_BYTES} bytes)"
