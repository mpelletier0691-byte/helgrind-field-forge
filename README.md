Helgrind ᛬ Ásvættir Field Forge

Norse-themed (Hel realm) optimization UI for field developers working away from HQ — tuned for ThinkPad T490, Cursor IDE, and isolated project environments.
Helgrind is a local device-control and optimization console that applies durable OS-level tuning without any cloud services or background daemons.
Launch

Double-click Helgrind on the Desktop, or run:
bash

~/asvaettir-device-opt/helgrind/launch-helgrind.sh

On first launch, Helgrind installs UI dependencies (python3-tk, CustomTkinter, JetBrains Mono).
UI
Element	Purpose
Toolbar (always visible)	Branding, workspace path, live status
Hel’s Purify (large green)	System clean — apt, journals, caches
Nine Forges	Full install, quick tune, scan, Cursor bind, dev tools, maintenance, reports
Mímisbrunnr Log	Bottom log well for live output
Helheim Review

Helheim Scan performs a safe audit and tags suspicious files under:
bash

~/asvaettir-device-opt/helheim-review/

A manifest.json is generated for manual review. Findings may include:

    Broken symlinks

    dpkg audit issues

    World-writable files

    Empty files

Helgrind never auto-removes files — all findings require human review.
Dev Armory Profiles

    Core Forge — git, build tools, ripgrep, tmux

    Node — Node 20 for Cursor workflows

    Python Lab — venv tooling

    Containers — Docker (warns on 8GB RAM)

    Cursor Support — inotify / watchers

    Field Security — ufw, fail2ban

Workspace

Default field project root:
bash

~/Asvaettir/workspace

You can set a custom path directly in the toolbar.
Installation (Open-Source Build)

Clone the repository:
bash

git clone https://github.com/mpelletier0691-byte/helgrind-field-forge.git
cd helgrind-field-forge

Install dependencies:
bash

sudo bash install-deps.sh

Run Helgrind:
bash

python3 helgrind/app.py

Requirements

    Linux Mint (recommended)

    Python 3.12+

    CustomTkinter

    python3-tk

    pkexec / PolicyKit

    TLP, zram-tools, systemd timers

All dependencies are installed automatically via install-deps.sh.
Disclaimer

Helgrind is not a daemon, not a cloud service, and not a remote management tool.
It applies durable OS-level configuration locally and operates entirely offline.
License

Apache-2.0 — see LICENSE for details.
