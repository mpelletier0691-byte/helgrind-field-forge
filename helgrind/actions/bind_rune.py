"""Bind Rune — fuse best 3 properties from selected forges."""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Callable, Optional

from helgrind.actions import auto_mend, cursor_tune, llm_tune, purify, scan
from helgrind.actions.runner import pkexec_run
from helgrind.forge_catalog import BIND_RUNE_NAMES, FORGES, ForgeProperty
from helgrind.paths import OPTIMIZE_SCRIPT, ROOT


@dataclass
class BindRune:
    name: str
    properties: list[ForgeProperty]
    source_forges: list[str]


def forge_bind_rune(selected_forge_ids: list[str], seed: Optional[str] = None) -> BindRune:
    """Pick best 3 properties from union of selected forges (stable random tie-break)."""
    pool: list[tuple[ForgeProperty, str]] = []
    for fid in selected_forge_ids:
        fdef = FORGES.get(fid)
        if fdef:
            for prop in fdef.properties:
                pool.append((prop, fid))

    if not pool:
        raise ValueError("No properties in selection")

    # Score sort with seeded shuffle among equals
    rng = random.Random(seed or "|".join(sorted(selected_forge_ids)))
    pool.sort(key=lambda x: (-x[0].score, rng.random()))

    seen_ids: set[str] = set()
    picked: list[ForgeProperty] = []
    sources: list[str] = []
    for prop, fid in pool:
        if prop.id in seen_ids:
            continue
        seen_ids.add(prop.id)
        picked.append(prop)
        if fid not in sources:
            sources.append(fid)
        if len(picked) >= 3:
            break

    name_idx = int(hashlib.sha256("|".join(selected_forge_ids).encode()).hexdigest(), 16) % len(BIND_RUNE_NAMES)
    return BindRune(name=BIND_RUNE_NAMES[name_idx], properties=picked, source_forges=selected_forge_ids)


def _exec_property(prop_id: str, log_cb: Optional[Callable[[str], None]]) -> None:
    if log_cb:
        log_cb(f"  • {prop_id}")

    if prop_id == "cache_purge" or prop_id == "journal_trim" or prop_id == "temp_sweep":
        purify.purify(log_cb)
    elif prop_id == "apt_heal" or prop_id == "quick_temper":
        if prop_id == "quick_temper":
            script = OPTIMIZE_SCRIPT if OPTIMIZE_SCRIPT.exists() else ROOT / "files" / "device-optimize.sh"
            if script.exists():
                pkexec_run(str(script), log_cb)
        else:
            from helgrind.actions.runner import run_bash
            run_bash(
                "dpkg --configure -a; apt-get -f install -y",
                log_cb,
            )
    elif prop_id == "helheim_scan":
        scan.scan_files()
    elif prop_id == "cursor_rules" or prop_id == "workspace" or prop_id == "node_heap":
        cursor_tune.apply_cursor_tune()
    elif prop_id == "ollama_caps" or prop_id == "llm_env" or prop_id == "cursor_hints":
        llm_tune.apply_llm_dev_mode()
    elif prop_id == "cpu_perf" or prop_id == "sysctl" or prop_id == "ssd_trim":
        script = OPTIMIZE_SCRIPT if OPTIMIZE_SCRIPT.exists() else ROOT / "files" / "device-optimize.sh"
        if script.exists():
            pkexec_run(str(script), log_cb)
    elif prop_id in ("symlink_hunt", "perm_audit", "dpkg_audit"):
        scan.scan_files()


def invoke_bind_rune(
    selected_forge_ids: list[str],
    log_cb: Optional[Callable[[str], None]] = None,
) -> tuple[bool, str]:
    if len(selected_forge_ids) < 2:
        return False, "Select at least 2 forges to bind a rune."

    rune = forge_bind_rune(selected_forge_ids)
    if log_cb:
        log_cb(f"᛭ Bind Rune forged: {rune.name}")
        log_cb(f"  Sources: {', '.join(rune.source_forges)}")
        for p in rune.properties:
            log_cb(f"  ᛬ {p.name} — {p.desc}")

    for prop in rune.properties:
        try:
            _exec_property(prop.id, log_cb)
        except Exception as e:
            if log_cb:
                log_cb(f"  ! {prop.id}: {e}")

    summary = (
        f"Bind Rune: {rune.name}\n\n"
        f"Forged from: {', '.join(rune.source_forges)}\n\n"
        "Properties:\n"
        + "\n".join(f"• {p.name}: {p.desc}" for p in rune.properties)
    )
    return True, summary


def run_selected_forges(
    selected_forge_ids: list[str],
    log_cb: Optional[Callable[[str], None]] = None,
) -> tuple[bool, str]:
    """Run each selected forge's full action in sequence."""
    if not selected_forge_ids:
        return False, "Nothing selected."

    from helgrind.actions import stack_tune

    runners = {
        "purify": lambda: purify.purify(log_cb),
        "auto_mend": lambda: auto_mend.auto_mend(log_cb),
        "cursor_bind": lambda: cursor_tune.apply_cursor_tune(),
        "llm_dev_mode": lambda: llm_tune.apply_llm_dev_mode(),
        "quick_temper": lambda: _quick_temper(log_cb),
        "helheim_scan": lambda: _helheim_scan(log_cb),
    }

    results: list[str] = []
    ok_all = True
    for fid in selected_forge_ids:
        if log_cb:
            log_cb(f"── {FORGES[fid].label} ──")
        fn = runners.get(fid)
        if not fn:
            continue
        ok, msg = fn()
        results.append(f"{FORGES[fid].label}: {'OK' if ok else 'FAIL'}")
        ok_all = ok_all and ok

    return ok_all, "Ran selected forges:\n" + "\n".join(results)


def _quick_temper(log_cb):
    script = OPTIMIZE_SCRIPT if OPTIMIZE_SCRIPT.exists() else ROOT / "files" / "device-optimize.sh"
    if not script.exists():
        return False, "Run Full Forge first."
    rc = pkexec_run(str(script), log_cb)
    return rc == 0, "temper"


def _helheim_scan(log_cb):
    m = scan.scan_files()
    return True, f"{m['count']} tagged"
