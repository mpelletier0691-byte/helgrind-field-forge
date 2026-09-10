# Helgrind ᛬ Asvaettir Field Forge

Norse-themed (Hel realm) optimization UI for **field developers** away from HQ — tuned for ThinkPad T490, Cursor, and isolated secret projects.

## Launch

Double-click **Helgrind** on the Desktop, or:

```bash
~/asvaettir-device-opt/helgrind/launch-helgrind.sh
```

First run installs UI dependencies (`python3-tk`, CustomTkinter, JetBrains Mono).

## UI

| Element | Purpose |
|--------|---------|
| **Toolbar** (always visible) | Branding, workspace path, live status |
| **Hel's Purify** (large green) | System clean — apt, journals, caches |
| **Nine Forges** | Full install, quick tune, scan, Cursor bind, dev tools, maintenance, reports |
| **Mímisbrunnr log** | Bottom log well |

## Helheim Review

**Helheim Scan** tags suspicious files under `~/asvaettir-device-opt/helheim-review/` with a `manifest.json` for your review (broken symlinks, dpkg issues, world-writable files, empty files).

## Dev Armory profiles

- **Core Forge** — git, build tools, ripgrep, tmux  
- **Node** — Node 20 for Cursor workflows  
- **Python Lab** — venv tooling  
- **Containers** — Docker (warns on 8GB RAM)  
- **Cursor Support** — inotify / watchers  
- **Field Security** — ufw, fail2ban  

## Workspace

Default field project root: `~/Asvaettir/workspace` (set path in toolbar).
