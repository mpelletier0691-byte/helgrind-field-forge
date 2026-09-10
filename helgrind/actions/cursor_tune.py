"""Cursor & Asvaettir field workflow tuning (user-level, no root)."""
from pathlib import Path

from helgrind.paths import CURSOR_CONFIG, DEV_WORKSPACE, HOME

ENV_FILE = HOME / ".config" / "environment.d" / "99-asvaettir-dev.conf"
CURSOR_RULES = HOME / ".cursor" / "rules" / "asvaettir-field.mdc"


def apply_cursor_tune() -> tuple[bool, str]:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(
        """# Asvaettir field developer — Cursor-optimized session
NODE_OPTIONS=--max-old-space-size=4096
UV_THREADPOOL_SIZE=8
MALLOC_ARENA_MAX=2
GIT_TERMINAL_PROMPT=0
EDITOR=cursor --wait
DELTA_FEATURES=side-by-side line-numbers
""",
        encoding="utf-8",
    )
    # Also apply LLM dev env (idempotent)
    from helgrind.actions import llm_tune
    llm_tune.apply_llm_dev_mode()

    CURSOR_RULES.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_RULES.write_text(
        """---
description: Asvaettir Labs field device — isolated dev from HQ
alwaysApply: true
---

# Field forge context

This machine is an **Asvaettir Labs field laptop** (ThinkPad T490, 8GB RAM).
Developer may run **isolated secret projects** away from HQ.

- Prefer lean builds; avoid Docker unless necessary.
- Respect `~/Asvaettir/workspace` as default project root.
- Use Helgrind for system health before blaming the toolchain.
""",
        encoding="utf-8",
    )

    DEV_WORKSPACE.mkdir(parents=True, exist_ok=True)
    gitignore = DEV_WORKSPACE / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n!README.md\n", encoding="utf-8")
    readme = DEV_WORKSPACE / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Asvaettir Field Workspace\n\n"
            "Isolated development root for projects away from HQ.\n",
            encoding="utf-8",
        )

    lines = [
        "Cursor & workflow tuning applied.",
        f"Environment: {ENV_FILE}",
        f"Cursor rule: {CURSOR_RULES}",
        f"Workspace: {DEV_WORKSPACE}",
    ]
    if CURSOR_CONFIG.exists():
        lines.append(f"Cursor config dir: {CURSOR_CONFIG}")
    return True, "\n".join(lines)
