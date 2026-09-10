"""Sync device state into Helgrind for recommendations."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from helgrind.paths import HOME, INSTALL_SCRIPT, OPTIMIZE_SCRIPT, REPORT, ROOT

SYNC_FILE = ROOT / "helgrind" / "device-sync.json"


def _run(cmd: list[str], timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr or "").strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def collect_device_state() -> dict:
    mem = _run(["free", "-h"])
    governor = ""
    gpath = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if gpath.exists():
        governor = gpath.read_text(encoding="utf-8").strip()

    swappiness = ""
    try:
        swappiness = Path("/proc/sys/vm/swappiness").read_text(encoding="utf-8").strip()
    except OSError:
        pass

    def has_cmd(c: str) -> bool:
        return shutil.which(c) is not None

    def pkg_installed(pattern: str) -> bool:
        out = _run(["dpkg", "-l"])
        return bool(re.search(rf"^ii\s+\S*{re.escape(pattern)}", out, re.M))

    env_files = [
        HOME / ".config/environment.d/99-asvaettir-dev.conf",
        HOME / ".config/environment.d/99-asvaettir-llm-dev.conf",
    ]

    return {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "hostname": os.uname().nodename,
        "ram_hint": mem.split("\n")[1] if mem else "unknown",
        "cpu_governor": governor or "unknown",
        "swappiness": swappiness,
        "full_forge_complete": (ROOT / ".install-complete").exists(),
        "optimize_script": OPTIMIZE_SCRIPT.exists(),
        "install_report": REPORT.exists(),
        "tools": {
            "git": has_cmd("git"),
            "node": has_cmd("node"),
            "ollama": has_cmd("ollama"),
            "docker": has_cmd("docker"),
            "podman": has_cmd("podman"),
            "gh": has_cmd("gh"),
            "uv": has_cmd("uv"),
            "lazygit": has_cmd("lazygit"),
            "delta": has_cmd("delta"),
            "direnv": has_cmd("direnv"),
        },
        "packages": {
            "tlp": pkg_installed("tlp"),
            "zram": pkg_installed("zram"),
            "earlyoom": pkg_installed("earlyoom"),
            "unattended": pkg_installed("unattended"),
        },
        "env_tunes": {p.name: p.exists() for p in env_files},
        "cursor_rules": (HOME / ".cursor/rules/asvaettir-field.mdc").exists(),
    }


def sync_device() -> tuple[bool, str]:
    SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = collect_device_state()
    with open(SYNC_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return True, f"Device synced.\n{SYNC_FILE}"


def load_sync() -> dict | None:
    if not SYNC_FILE.exists():
        return None
    try:
        return json.loads(SYNC_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
