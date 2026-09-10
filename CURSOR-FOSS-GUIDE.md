# Helgrind — Cursor + LLM + FOSS guide (T490 / 8GB)

## Recommended order

1. **Full Forge** — system performance base  
2. **LLM Dev Mode** — env vars for Cursor + Ollama (no password)  
3. **Cursor Bind** — rules + workspace  
4. **Dev Armory** — pick kits below  

## Best bang-for-RAM (install first)

| Kit | Why |
|-----|-----|
| OOM Guard | Stops freezes when Cursor + builds eat RAM |
| Cursor Git Stack | gh, delta, lazygit, direnv |
| Cursor Support | Watchers + shellcheck for AI edits |
| Core Forge | Standard CLI dev tools |

## Local LLM on 8GB

| Kit | Notes |
|-----|--------|
| Ollama | FOSS; use **small** models only |
| LLM system tune | Extra sysctl |

Use **cloud models in Cursor** for heavy work; local Ollama for offline/small tasks.

## Actual desktop apps (FOSS)

| App | Menu name | Use with Cursor |
|-----|-----------|-----------------|
| **Meld** | Meld | Visual diff for AI changes |
| **DB Browser** | DB Browser for SQLite | Inspect SQLite DBs |
| **Gitg** | Gitg | Git history GUI |
| **Bruno** | Bruno (Flatpak) | Test REST/LLM APIs |

Install **Flatpak** first if Bruno fails.

## Not installed (use Cursor instead)

- Second code editor — Cursor is enough  
- Docker Desktop — use **Podman** profile unless required  

## Continue.dev (optional)

Install **Continue** extension inside Cursor to connect Ollama/local models — not bundled in Helgrind.
