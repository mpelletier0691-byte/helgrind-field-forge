"""Scan for faulty files and tag for Helheim review."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from helgrind.paths import HOME, REVIEW_DIR, REVIEW_MANIFEST

SKIP_DIRS = {
    "/proc", "/sys", "/dev", "/run", "/snap", "/var/lib/docker",
    "/usr/lib", "/usr/share", "/opt", "/boot",
}


def _should_skip(path: Path) -> bool:
    parts = path.parts
    for skip in SKIP_DIRS:
        if str(path).startswith(skip):
            return True
    skip_names = {
        ".cache", "node_modules", ".git", ".mozilla", ".venv", ".npm",
        ".local", "snap", "__pycache__", ".cursor",
    }
    if skip_names & set(parts):
        return True
    if "helgrind" in parts and ".venv" in parts:
        return True
    return False


def scan_files(
    roots: Optional[list[Path]] = None,
    progress_cb: Optional[Callable[[str, float], None]] = None,
) -> dict:
    roots = roots or [HOME, HOME / "Asvaettir", HOME / "Documents", HOME / "Desktop"]
    findings: list[dict] = []
    scanned = 0

    def report(msg: str, pct: float) -> None:
        if progress_cb:
            progress_cb(msg, pct)

    report("Checking package health…", 0.05)
    try:
        r = subprocess.run(
            ["dpkg", "--audit"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.stdout.strip():
            findings.append({
                "path": "(system)",
                "kind": "dpkg_broken",
                "severity": "high",
                "detail": r.stdout.strip()[:500],
            })
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    report("Scanning broken symlinks…", 0.15)
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            if _should_skip(Path(dirpath)):
                dirnames.clear()
                continue
            scanned += 1
            if scanned % 200 == 0 and progress_cb:
                progress_cb(f"Scanning {dirpath[:60]}…", min(0.15 + (scanned % 1000) / 5000, 0.85))

            for name in filenames + dirnames:
                p = Path(dirpath) / name
                if name in (".", ".."):
                    continue
                if p.is_symlink() and not p.exists():
                    findings.append({
                        "path": str(p),
                        "kind": "broken_symlink",
                        "severity": "medium",
                        "detail": "Symlink target missing",
                    })

            for name in filenames:
                p = Path(dirpath) / name
                try:
                    if p.is_file() and p.stat().st_size == 0 and p.suffix not in (".keep",):
                        if "placeholder" not in p.name.lower():
                            findings.append({
                                "path": str(p),
                                "kind": "zero_byte",
                                "severity": "low",
                                "detail": "Empty file (may be intentional)",
                            })
                except OSError:
                    findings.append({
                        "path": str(p),
                        "kind": "unreadable",
                        "severity": "high",
                        "detail": "Cannot read file metadata",
                    })

    report("Checking world-writable files in home…", 0.9)
    try:
        r = subprocess.run(
            ["find", str(HOME), "-maxdepth", "4", "-type", "f", "-perm", "-0002"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        for line in r.stdout.strip().splitlines()[:50]:
            if line and not _should_skip(Path(line)):
                findings.append({
                    "path": line,
                    "kind": "world_writable",
                    "severity": "medium",
                    "detail": "File is world-writable (security risk)",
                })
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    manifest = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "roots": [str(r) for r in roots],
        "count": len(findings),
        "items": findings,
    }

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with open(REVIEW_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    for i, item in enumerate(findings[:200]):
        tag = REVIEW_DIR / f"{i:04d}_{item['kind']}.tag"
        tag.write_text(
            f"path={item['path']}\nkind={item['kind']}\n"
            f"severity={item['severity']}\ndetail={item['detail']}\n",
            encoding="utf-8",
        )

    report("Scan complete.", 1.0)
    return manifest
