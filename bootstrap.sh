#!/bin/bash
# GUI-only bootstrap — zenity progress + pkexec (no terminal).
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"
LOG="$DIR/bootstrap.log"

log() { echo "$(date -Iseconds) $*" >>"$LOG"; }

install_tk() {
  python3 -c "import tkinter" 2>/dev/null && return 0
  log "apt: python3-tk"
  pkexec env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-tk python3-pip python3-venv fonts-jetbrains-mono >>"$LOG" 2>&1
  python3 -c "import tkinter" 2>/dev/null
}

install_venv() {
  if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "import customtkinter" 2>/dev/null; then
    return 0
  fi
  log "venv + pip"
  python3 -m venv "$VENV" >>"$LOG" 2>&1
  "$VENV/bin/pip" install -q --upgrade pip >>"$LOG" 2>&1
  "$VENV/bin/pip" install -q -r "$DIR/requirements.txt" >>"$LOG" 2>&1
  "$VENV/bin/python" -c "import customtkinter" 2>/dev/null
}

run_steps() {
  echo "# ᛬ Preparing the forge…"
  echo "8"
  install_tk || return 1
  echo "# ᛬ Binding runes…"
  echo "55"
  install_venv || return 1
  echo "# ᛬ Helgrind ready"
  echo "100"
  return 0
}

if command -v zenity >/dev/null 2>&1; then
  if ! run_steps | zenity --progress --title="Helgrind" --percentage=0 --auto-close --width=400; then
    zenity --error --title="Helgrind" --text="Setup failed.\nLog: $LOG" 2>/dev/null || true
    exit 1
  fi
else
  run_steps >/dev/null || exit 1
fi

if ! "$VENV/bin/python" -c "import customtkinter" 2>/dev/null; then
  exit 1
fi
