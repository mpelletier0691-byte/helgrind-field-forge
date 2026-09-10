"""Auto Mend — scan, repair apt/dpkg, optimize, light purify (one-click)."""
from helgrind.actions import purify, scan
from helgrind.actions.runner import run_bash, pkexec_run
from helgrind.paths import OPTIMIZE_SCRIPT, ROOT


def auto_mend(log_cb=None) -> tuple[bool, str]:
    lines: list[str] = []

    if log_cb:
        log_cb("Helheim scan…")
    manifest = scan.scan_files(progress_cb=lambda m, p: log_cb and log_cb(m))
    lines.append(f"Scan: {manifest['count']} items tagged for review.")

    repair_script = """
export DEBIAN_FRONTEND=noninteractive
for f in /etc/apt/sources.list.d/cursor*.list; do
  [ -f "$f" ] && [[ "$f" != *.disabled* ]] && mv "$f" "${f}.disabled-by-asvaettir"
done
apt-get update -qq 2>/dev/null || true
dpkg --configure -a 2>/dev/null || true
apt-get -f install -y 2>/dev/null || true
"""
    if log_cb:
        log_cb("Repairing packages…")
    run_bash(repair_script, log_cb)

    opt = OPTIMIZE_SCRIPT if OPTIMIZE_SCRIPT.exists() else ROOT / "files" / "device-optimize.sh"
    if opt.exists():
        if log_cb:
            log_cb("Quick temper…")
        pkexec_run(str(opt), log_cb)

    if log_cb:
        log_cb("Purify…")
    ok_p, msg_p = purify.purify(log_cb)
    lines.append(msg_p)

    summary = "Auto Mend complete.\n" + "\n".join(lines)
    return ok_p, summary
