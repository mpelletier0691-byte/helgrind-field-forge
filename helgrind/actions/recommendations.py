"""Recommendations from synced device state."""
from __future__ import annotations

from dataclasses import dataclass

from helgrind.actions.device_sync import collect_device_state, load_sync


@dataclass
class Recommendation:
    title: str
    reason: str
    action: str  # forge id or armory profile id
    kind: str  # "forge" | "armory" | "bind" | "sync"


def build_recommendations(state: dict | None = None) -> list[Recommendation]:
    state = state or load_sync() or collect_device_state()
    recs: list[Recommendation] = []

    if not state.get("full_forge_complete"):
        recs.append(Recommendation(
            "Run Full Forge",
            "Base performance stack not installed yet.",
            "full_forge", "forge",
        ))

    if not state.get("packages", {}).get("earlyoom"):
        recs.append(Recommendation(
            "Install OOM Guard",
            "8GB RAM + Cursor: earlyoom prevents freezes.",
            "oom_guard", "armory",
        ))

    if not state.get("tools", {}).get("git"):
        recs.append(Recommendation(
            "Core Forge kit",
            "Git and build tools missing for field dev.",
            "core", "armory",
        ))

    if not state.get("tools", {}).get("gh"):
        recs.append(Recommendation(
            "Cursor Git Stack",
            "GitHub CLI + delta improve Cursor git workflow.",
            "cursor_git", "armory",
        ))

    if not state.get("env_tunes", {}).get("99-asvaettir-dev.conf"):
        recs.append(Recommendation(
            "Cursor Bind",
            "Cursor workspace & env not configured.",
            "cursor_bind", "forge",
        ))

    if not state.get("env_tunes", {}).get("99-asvaettir-llm-dev.conf"):
        recs.append(Recommendation(
            "LLM Dev Mode",
            "Local LLM / Cursor AI memory caps not set.",
            "llm_dev_mode", "forge",
        ))

    if state.get("cpu_governor") == "powersave" and state.get("optimize_script"):
        recs.append(Recommendation(
            "Quick Temper",
            "CPU still on powersave — boost for dev work.",
            "quick_temper", "forge",
        ))

    if int(state.get("swappiness") or "60") > 20:
        recs.append(Recommendation(
            "Auto Mend",
            "Swappiness high — run mend + sysctl tune.",
            "auto_mend", "forge",
        ))

    if not state.get("tools", {}).get("node"):
        recs.append(Recommendation(
            "Node 20 LTS",
            "Node missing — needed for many Cursor projects.",
            "node", "armory",
        ))

    if state.get("tools", {}).get("docker") and not state.get("tools", {}).get("podman"):
        recs.append(Recommendation(
            "Consider Podman",
            "Docker is heavy on 8GB; Podman is lighter.",
            "podman_light", "armory",
        ))

    if len(recs) >= 2:
        recs.insert(0, Recommendation(
            "Forge a Bind Rune",
            f"{len(recs)} gaps found — select 2+ forges, then invoke Bind Rune.",
            "bind_rune", "bind",
        ))

    if not recs:
        recs.append(Recommendation(
            "Device looks tuned",
            "Run Helheim Scan periodically or Purify weekly.",
            "helheim_scan", "forge",
        ))

    return recs[:12]


def format_recommendations_text(recs: list[Recommendation]) -> str:
    lines = ["᛬ Mímir recommends:\n"]
    for i, r in enumerate(recs, 1):
        lines.append(f"{i}. {r.title}\n   {r.reason}")
    return "\n".join(lines)
