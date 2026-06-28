#!/usr/bin/env bash
# Generate the nursing Flutter fallback asset from the backend seed bank.
#
# Usage: ./scripts/generate_nursing_flutter_assets.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${REPO_ROOT}/output/nursing_staff_nurse_output.json"
TARGET="${REPO_ROOT}/mathwise_build/assets/nursing/nursing_seed_questions.json"

if [[ ! -f "$SOURCE" ]]; then
  echo "Error: source seed bank not found at $SOURCE"
  echo "Generate or copy the nursing output first."
  exit 1
fi

python3 - <<PY
import json
import sys

with open("$SOURCE", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data.get("questions", [])
if not questions:
    print("Error: no questions found in source", file=sys.stderr)
    sys.exit(1)

with open("$TARGET", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, separators=(",", ":"))

size_kb = len(json.dumps(questions, ensure_ascii=False, separators=(",", ":"))) / 1024
print(f"Generated $TARGET")
print(f"  Questions: {len(questions)}")
print(f"  Size: {size_kb:.1f} KB")
PY
