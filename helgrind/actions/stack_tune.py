"""Apply multiple Helgrind tunes in one action."""
from typing import Callable, Optional

from helgrind.actions import cursor_tune, llm_tune
from helgrind.actions.dev_tools import DEV_PROFILES, install_profile
from helgrind.actions.install_helpers import APT_SKIP, LAZYGIT_INSTALL

# One password — installs these apt profiles in a single pkexec run
RECOMMENDED_DEV_KIT = [
    "oom_guard",
    "core",
    "cursor_support",
    "cursor_git",
    "dev_monitor",
]


def apply_all_config_tunes() -> tuple[bool, str]:
    """No root — stacks Cursor Bind + LLM Dev Mode env/rules."""
    lines: list[str] = []
    ok1, msg1 = cursor_tune.apply_cursor_tune()
    lines.append(msg1)
    ok2, msg2 = llm_tune.apply_llm_dev_mode()
    if msg2 not in msg1:
        lines.append(msg2)
    return ok1 and ok2, "Applied config tunes (stacked):\n\n" + "\n\n".join(lines)


def install_recommended_kit(log_cb: Optional[Callable[[str], None]] = None) -> tuple[bool, str]:
    """One admin prompt — installs the recommended Dev Armory profiles."""
    labels = [DEV_PROFILES[p]["label"] for p in RECOMMENDED_DEV_KIT if p in DEV_PROFILES]
    if log_cb:
        log_cb(f"Installing kit: {', '.join(labels)}")

    body = "export DEBIAN_FRONTEND=noninteractive\n"
    body += "for f in /etc/apt/sources.list.d/cursor*.list; do "
    body += '[ -f "$f" ] && [[ "$f" != *.disabled* ]] && mv "$f" "${f}.disabled-by-asvaettir"; done\n'
    body += "apt-get update -qq || true\n"

    all_packages: list[str] = []
    scripts: list[str] = []
    for pid in RECOMMENDED_DEV_KIT:
        p = DEV_PROFILES.get(pid)
        if not p:
            continue
        if p.get("packages"):
            all_packages.extend(p["packages"].split())
        if p.get("script"):
            scripts.append(f"# --- {pid} ---\n{p['script']}")

    apt_pkgs = [p for p in dict.fromkeys(all_packages) if p not in APT_SKIP]
    if apt_pkgs:
        body += f"apt-get install -y {' '.join(apt_pkgs)}\n"

    # lazygit not in Mint repos — always run helper if cursor_git in kit
    if "cursor_git" in RECOMMENDED_DEV_KIT:
        body += LAZYGIT_INSTALL + "\n"

    for script in scripts:
        if "install_lazygit" not in script:  # avoid duplicate
            body += script + "\n"

    body += 'echo "Recommended kit finished."\n'

    from helgrind.actions.runner import run_bash

    rc = run_bash(body, log_cb)
    summary = "Recommended field kit:\n• " + "\n• ".join(labels)
    notes = []
    if rc != 0:
        notes.append(f"Some steps exited with code {rc} — check log above.")
    notes.append("lazygit: via apt or GitHub if Cursor Git Stack was included.")
    return rc == 0, summary + "\n\n" + "\n".join(notes)
