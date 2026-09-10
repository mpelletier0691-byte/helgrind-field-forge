"""Forge definitions, bind-rune properties, and execution hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

# Forges that toggle-select (not Dev Armory / Full Forge)
SELECTABLE_FORGES = frozenset({
    "purify", "auto_mend", "cursor_bind", "llm_dev_mode", "quick_temper", "helheim_scan",
})

BIND_RUNE_NAMES = (
    "Hel's Covenant", "Nifl Bind", "Surtr's Chain", "Mímir's Knot",
    "Jörmungandr Loop", "Fenrir's Pact", "Skuld's Weave",
)


@dataclass(frozen=True)
class ForgeProperty:
    id: str
    name: str
    score: int
    desc: str


@dataclass(frozen=True)
class ForgeDef:
    id: str
    rune: str
    label: str
    sub: str
    color: str
    hover: str
    properties: tuple[ForgeProperty, ...]


FORGES: dict[str, ForgeDef] = {
    "purify": ForgeDef(
        "purify", "✦", "Purify", "clean", "#15803d", "#22c55e",
        (
            ForgeProperty("cache_purge", "Cache Purge", 92, "Drop page cache & apt cruft"),
            ForgeProperty("journal_trim", "Journal Trim", 88, "Shrink systemd logs"),
            ForgeProperty("temp_sweep", "Temp Sweep", 85, "Clear temp thumbnails"),
        ),
    ),
    "auto_mend": ForgeDef(
        "auto_mend", "ᛉ", "Auto Mend", "fix+tune", "#7c3aed", "#8b5cf6",
        (
            ForgeProperty("apt_heal", "Apt Heal", 95, "Repair broken packages"),
            ForgeProperty("helheim_scan", "Helheim Scan", 90, "Tag faulty files"),
            ForgeProperty("quick_temper", "Quick Temper", 87, "CPU & sysctl boost"),
        ),
    ),
    "cursor_bind": ForgeDef(
        "cursor_bind", "ᚱ", "Cursor Bind", "workflow", "#059669", "#34d399",
        (
            ForgeProperty("cursor_rules", "Cursor Rules", 93, "Field dev AI context"),
            ForgeProperty("workspace", "Workspace Root", 88, "Asvaettir project path"),
            ForgeProperty("node_heap", "Node Heap Cap", 86, "4GB max for extensions"),
        ),
    ),
    "llm_dev_mode": ForgeDef(
        "llm_dev_mode", "ᛚ", "LLM Dev Mode", "AI tuning", "#0d9488", "#14b8a6",
        (
            ForgeProperty("ollama_caps", "Ollama Caps", 94, "Limit parallel models"),
            ForgeProperty("llm_env", "LLM Env Stack", 91, "Inference-friendly vars"),
            ForgeProperty("cursor_hints", "Cursor Hints", 84, "AI settings guide"),
        ),
    ),
    "quick_temper": ForgeDef(
        "quick_temper", "ᛊ", "Quick Temper", "boost", "#334155", "#475569",
        (
            ForgeProperty("cpu_perf", "CPU Performance", 96, "Governor on AC"),
            ForgeProperty("sysctl", "Sysctl Tune", 89, "Swappiness & watchers"),
            ForgeProperty("ssd_trim", "SSD Trim", 82, "fstrim if supported"),
        ),
    ),
    "helheim_scan": ForgeDef(
        "helheim_scan", "ᛟ", "Helheim Scan", "review", "#4c1d95", "#6d28d9",
        (
            ForgeProperty("symlink_hunt", "Symlink Hunt", 90, "Broken links"),
            ForgeProperty("perm_audit", "Perm Audit", 88, "World-writable files"),
            ForgeProperty("dpkg_audit", "Dpkg Audit", 86, "Package integrity"),
        ),
    ),
}
