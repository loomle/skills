#!/usr/bin/env bash
set -euo pipefail

# Run UnrealEditor-Cmd Python script and enforce DONE marker presence.
# Usage:
#   run_ue_python_and_check_done.sh <uproject> <python_script_abs_path> <done_marker> <log_path>

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <uproject> <python_script_abs_path> <done_marker> <log_path>" >&2
  exit 2
fi

UPROJECT="$1"
PY_SCRIPT="$2"
DONE_MARKER="$3"
LOG_PATH="$4"
UE_BIN="${UE_BIN:-}"

if [[ -z "$UE_BIN" ]]; then
  if command -v UnrealEditor-Cmd >/dev/null 2>&1; then
    UE_BIN="$(command -v UnrealEditor-Cmd)"
  else
    echo "[FAIL] UnrealEditor-Cmd not found. Set UE_BIN env var or add UnrealEditor-Cmd to PATH." >&2
    exit 2
  fi
fi

mkdir -p "$(dirname "$LOG_PATH")"

"$UE_BIN" "$UPROJECT" -run=pythonscript -script="$PY_SCRIPT" -unattended -nop4 -nosplash -nullrhi -stdout > "$LOG_PATH" 2>&1

if ! rg -q "$DONE_MARKER" "$LOG_PATH"; then
  echo "[FAIL] DONE marker not found: $DONE_MARKER" >&2
  echo "[INFO] log: $LOG_PATH" >&2
  exit 1
fi

echo "[OK] DONE marker found: $DONE_MARKER"
echo "[INFO] log: $LOG_PATH"
