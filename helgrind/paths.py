"""Canonical paths for Helgrind."""
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "asvaettir-device-opt"
HELGRIND = ROOT / "helgrind"
REVIEW_DIR = ROOT / "helheim-review"
REVIEW_MANIFEST = REVIEW_DIR / "manifest.json"
LOG_DIR = ROOT / "logs"
INSTALL_SCRIPT = ROOT / "install-asvaettir-optimization.sh"
OPTIMIZE_SCRIPT = Path("/opt/asvaettir-labs/device-optimize.sh")
MAINTENANCE_SCRIPT = Path("/opt/asvaettir-labs/maintenance.sh")
REPORT = ROOT / "install-report.txt"
DEV_WORKSPACE = HOME / "Asvaettir" / "workspace"
CURSOR_CONFIG = HOME / ".config" / "Cursor"
SYNC_FILE = HELGRIND / "device-sync.json"

for d in (REVIEW_DIR, LOG_DIR, DEV_WORKSPACE):
    d.mkdir(parents=True, exist_ok=True)
