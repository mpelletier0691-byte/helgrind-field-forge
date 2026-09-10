"""System clean — Hel's Purify (green action)."""
from datetime import datetime

from helgrind.actions.runner import run_bash
from helgrind.paths import LOG_DIR

LOG = LOG_DIR / "purify.log"


def purify(log_cb=None) -> tuple[bool, str]:
    ts = datetime.now().isoformat()
    script = f"""
echo "=== Helgrind Purify {ts} ==="
apt-get clean -y 2>/dev/null || true
apt-get autoclean -y 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true
journalctl --vacuum-time=7d 2>/dev/null || journalctl --vacuum-size=300M 2>/dev/null || true
rm -rf /tmp/* 2>/dev/null || true
rm -rf "$HOME/.cache/thumbnails/"* 2>/dev/null || true
find "$HOME/.cache" -type f -atime +30 -delete 2>/dev/null || true
sync
if [ -w /proc/sys/vm/drop_caches ]; then echo 3 > /proc/sys/vm/drop_caches; fi
echo "Purify complete."
"""
    rc = run_bash(script, log_cb)
    summary = f"Purify finished (exit {rc}). Log: {LOG}"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n{ts} exit={rc}\n")
    return rc == 0, summary
