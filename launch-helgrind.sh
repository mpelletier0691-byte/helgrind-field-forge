#!/bin/bash
# Launch Helgrind as a native GUI window only — never opens a terminal.
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"
export PYTHONPATH="$DIR${PYTHONPATH:+:$PYTHONPATH}"
export DISPLAY="${DISPLAY:-:0}"

cd "$DIR"

needs_bootstrap() {
  ! python3 -c "import tkinter" 2>/dev/null && return 0
  ! [ -x "$VENV/bin/python" ] && return 0
  ! "$VENV/bin/python" -c "import customtkinter" 2>/dev/null && return 0
  return 1
}

if needs_bootstrap; then
  bash "$DIR/bootstrap.sh" || exit 1
fi

exec "$VENV/bin/python" -m helgrind 2>>"$DIR/helgrind.log"
