"""LLM + dev-mode tuning for Cursor and optional local inference (8GB-safe)."""
from pathlib import Path

from helgrind.paths import HOME

ENV_FILE = HOME / ".config" / "environment.d" / "99-asvaettir-llm-dev.conf"
CURSOR_SETTINGS_HINT = HOME / ".config" / "Cursor" / "User" / "helgrind-hints.txt"


def apply_llm_dev_mode() -> tuple[bool, str]:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(
        """# Helgrind LLM + dev mode (8GB ThinkPad T490)
# Cursor / Node
NODE_OPTIONS=--max-old-space-size=4096
UV_THREADPOOL_SIZE=8
MALLOC_ARENA_MAX=2

# Local LLM (Ollama) — keep memory predictable
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_KEEP_ALIVE=5m
OLLAMA_FLASH_ATTENTION=1

# Git / tooling
GIT_TERMINAL_PROMPT=0
DELTA_FEATURES=side-by-side line-numbers
EDITOR=cursor --wait
""",
        encoding="utf-8",
    )

    CURSOR_SETTINGS_HINT.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_SETTINGS_HINT.write_text(
        """Helgrind — suggested Cursor settings (set in Cursor → Settings):

• Files: Watcher Exclude large folders (node_modules, .git, dist, models)
• Search: Exclude same paths
• AI: Prefer cloud models on 8GB RAM; local Ollama only for small models
• Terminal: Integrated GPU acceleration off if UI stutters
• Extensions: Disable unused language servers on field laptop

Re-run Helgrind → Cursor Bind after changes.
""",
        encoding="utf-8",
    )

    return True, (
        "LLM dev mode applied (logout/login or reboot for env vars).\n"
        f"Env: {ENV_FILE}\n"
        f"Cursor hints: {CURSOR_SETTINGS_HINT}"
    )
