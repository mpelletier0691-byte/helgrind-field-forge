"""Curated dev tools — FOSS, Cursor-friendly, T490 / 8GB aware."""
from helgrind.actions.install_helpers import APT_SKIP, LAZYGIT_INSTALL
from helgrind.actions.runner import run_bash

# Display order with section headers in Dev Armory
DEV_SECTIONS: list[tuple[str, list[str]]] = [
    ("᛬ Performance & dev mode", ["oom_guard", "dev_monitor", "podman_light"]),
    ("᛬ Cursor & Git workflow", ["core", "cursor_git", "cursor_support", "node", "python_fast", "python"]),
    ("᛬ Local LLM (optional)", ["ollama", "llm_sys_tune"]),
    ("᛬ GUI apps (free & open source)", ["gui_diff", "gui_db", "gui_git", "gui_api", "flatpak_base"]),
    ("᛬ Security", ["security"]),
]

DEV_PROFILES: dict[str, dict] = {
    "oom_guard": {
        "label": "OOM Guard",
        "desc": "earlyoom — frees RAM before freeze when Cursor + builds spike memory.",
        "packages": "earlyoom",
        "script": """
systemctl enable earlyoom 2>/dev/null || true
systemctl restart earlyoom 2>/dev/null || true
""",
    },
    "dev_monitor": {
        "label": "Dev Monitor",
        "desc": "btop + ncdu — live CPU/RAM view and disk usage (terminal).",
        "packages": "btop ncdu htop",
    },
    "podman_light": {
        "label": "Podman (lighter containers)",
        "desc": "Rootless containers — often better than Docker on 8GB RAM.",
        "packages": "podman podman-compose",
        "warn": "Still heavy; stop unused containers when using Cursor AI.",
    },
    "core": {
        "label": "Core Forge",
        "desc": "git, build-essential, curl, jq, ripgrep, fd-find, tmux.",
        "packages": "git build-essential curl wget jq ripgrep fd-find tmux unzip",
    },
    "cursor_git": {
        "label": "Cursor Git Stack",
        "desc": "GitHub CLI (gh), git-delta, direnv, lazygit — diffs & repos from terminal.",
        "packages": "gh git-delta direnv",
        "script": LAZYGIT_INSTALL,
    },
    "cursor_support": {
        "label": "Cursor Support",
        "desc": "inotify-tools, shellcheck — file watchers & shell linting for AI edits.",
        "packages": "inotify-tools shellcheck",
        "script": """
CONF=/etc/sysctl.d/99-asvaettir-performance.conf
grep -q fs.inotify.max_user_watches "$CONF" 2>/dev/null || {
  echo 'fs.inotify.max_user_watches=524288' >> "$CONF"
  sysctl -p "$CONF" 2>/dev/null || true
}
""",
    },
    "node": {
        "label": "Node 20 LTS",
        "desc": "Node.js for Cursor extensions, npm, pnpm, yarn.",
        "script": """
export DEBIAN_FRONTEND=noninteractive
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g npm@latest pnpm yarn 2>/dev/null || true
""",
    },
    "python_fast": {
        "label": "uv (fast Python)",
        "desc": "Astral uv — fastest pip/venv tool; great with Cursor Python projects.",
        "script": r"""
export DEBIAN_FRONTEND=noninteractive
apt-get install -y curl
RUN_USER="${SUDO_USER:-asvaettir-labs}"
[ -n "${PKEXEC_UID:-}" ] && RUN_USER=$(id -nu "$PKEXEC_UID" 2>/dev/null) || true
sudo -u "$RUN_USER" bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
""",
    },
    "python": {
        "label": "Python Lab",
        "desc": "python3, pip, venv, dev headers.",
        "packages": "python3 python3-pip python3-venv python3-dev",
    },
    "ollama": {
        "label": "Ollama (local LLM)",
        "desc": "Run open models locally — pair with Cursor via Continue or API.",
        "warn": "8GB RAM: use tiny models only (phi3, gemma2:2b). Close Cursor for large pulls.",
        "script": """
export DEBIAN_FRONTEND=noninteractive
curl -fsSL https://ollama.com/install.sh | sh
systemctl enable ollama 2>/dev/null || true
""",
    },
    "llm_sys_tune": {
        "label": "LLM system tune",
        "desc": "Extra sysctl for responsiveness under AI + compile load.",
        "script": """
CONF=/etc/sysctl.d/99-asvaettir-llm.conf
cat > "$CONF" <<'EOF'
# Helgrind LLM/dev responsiveness
vm.swappiness=10
vm.vfs_cache_pressure=50
kernel.sched_autogroup_enabled=0
EOF
sysctl -p "$CONF" 2>/dev/null || true
""",
    },
    "gui_diff": {
        "label": "Meld",
        "desc": "Visual diff/merge tool — review Cursor multi-file edits.",
        "packages": "meld",
    },
    "gui_db": {
        "label": "DB Browser for SQLite",
        "desc": "GUI for SQLite — inspect app DBs without leaving desktop.",
        "packages": "sqlitebrowser",
    },
    "gui_git": {
        "label": "Gitg",
        "desc": "Simple Git history browser — complement to Cursor source control.",
        "packages": "gitg",
    },
    "gui_api": {
        "label": "Bruno (API client)",
        "desc": "FOSS Postman alternative — test APIs for LLM backends & services.",
        "warn": "Installs Flatpak if needed (~200MB).",
        "script": """
export DEBIAN_FRONTEND=noninteractive
apt-get install -y flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub com.usebruno.Bruno
""",
    },
    "flatpak_base": {
        "label": "Flatpak (app store)",
        "desc": "Required for Bruno and other sandboxed FOSS apps.",
        "packages": "flatpak",
        "script": "flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo",
    },
    "docker": {
        "label": "Docker (heavy)",
        "desc": "Docker CE — prefer Podman on 8GB unless you need Docker exactly.",
        "packages": "docker.io docker-compose-v2",
        "warn": "8GB RAM: heavy. Use Podman profile when possible.",
    },
    "security": {
        "label": "Field Security",
        "desc": "ufw firewall + fail2ban.",
        "packages": "ufw fail2ban",
    },
}


def all_profile_ids() -> list[str]:
    ids: list[str] = []
    for _, group in DEV_SECTIONS:
        ids.extend(group)
    return ids


def install_profile(profile_id: str, log_cb=None) -> tuple[bool, str]:
    if profile_id not in DEV_PROFILES:
        return False, f"Unknown profile: {profile_id}"
    p = DEV_PROFILES[profile_id]
    body = "export DEBIAN_FRONTEND=noninteractive\n"
    body += "for f in /etc/apt/sources.list.d/cursor*.list; do "
    body += '[ -f "$f" ] && [[ "$f" != *.disabled* ]] && mv "$f" "${f}.disabled-by-asvaettir"; done\n'
    body += "apt-get update -qq || true\n"
    if p.get("packages"):
        body += f"apt-get install -y {p['packages']}\n"
    if p.get("script"):
        body += p["script"] + "\n"
    body += f'echo "Installed: {profile_id}"\n'
    rc = run_bash(body, log_cb)
    msg = p.get("warn", "")
    if rc == 0:
        return True, f"Installed: {p['label']}. {msg}".strip()
    return False, f"Install failed for {p['label']} (exit {rc}). {msg}".strip()
