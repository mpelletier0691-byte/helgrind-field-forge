#!/usr/bin/env python3
"""Helgrind — field device optimizer with bind runes & device sync."""
from __future__ import annotations

import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from helgrind import theme as T
from helgrind.actions import auto_mend, cursor_tune, dev_tools, purify, scan, stack_tune
from helgrind.actions import bind_rune, device_sync, recommendations
from helgrind.actions.runner import pkexec_run
from helgrind.forge_catalog import FORGES, ForgeDef
from helgrind.paths import DEV_WORKSPACE, INSTALL_SCRIPT, OPTIMIZE_SCRIPT, REPORT, ROOT
from helgrind.widgets import InstantForgeBubble, SelectableForgeBubble

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
ctk.set_widget_scaling(T.WIDGET_SCALING)
ctk.set_window_scaling(T.WINDOW_SCALING)


class HelgrindApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{T.APP_NAME} — {T.APP_SUBTITLE}")
        self.geometry("1080x820")
        self.minsize(980, 740)
        self.configure(fg_color=T.BG_DARK)

        self._busy = False
        self._selected: set[str] = set()
        self._forge_widgets: dict[str, SelectableForgeBubble] = {}
        self._bind_rune_frame: Optional[ctk.CTkFrame] = None
        self._bind_btn: Optional[ctk.CTkButton] = None
        self._invoke_btn: Optional[ctk.CTkButton] = None
        self._sync_state: Optional[dict] = None

        self._status = tk.StringVar(value="᛬ Tap forges to select · Sync for counsel")
        self._workspace = tk.StringVar(value=str(DEV_WORKSPACE))
        self._selection_label = tk.StringVar(value="Selected: 0")

        self._build_toolbar()
        self._build_bubbles()
        self._build_log()
        self.after(500, self._auto_sync)

    def _build_toolbar(self) -> None:
        bar = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=T.BG_TOOLBAR)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="᛬ HELGRIND", font=T.FONT_DISPLAY, text_color=T.ACCENT_HEL).pack(
            side="left", padx=(16, 4), pady=6,
        )

        acts = ctk.CTkFrame(bar, fg_color="transparent")
        acts.pack(side="left", padx=8)
        ctk.CTkButton(
            acts, text="Sync device", width=110, height=36, font=T.FONT_BODY,
            fg_color="#1e3a5f", hover_color=T.ACCENT_ICE, command=self._sync_device,
        ).pack(side="left", padx=3)
        ctk.CTkButton(
            acts, text="Counsel", width=88, height=36, font=T.FONT_BODY,
            fg_color=T.BORDER, hover_color=T.ACCENT_RUNE, command=self._show_counsel,
        ).pack(side="left", padx=3)
        self._invoke_btn = ctk.CTkButton(
            acts, text="Invoke selected", width=130, height=36, font=T.FONT_BODY,
            fg_color="#334155", hover_color="#64748b", state="disabled",
            command=self._invoke_selected,
        )
        self._invoke_btn.pack(side="left", padx=3)
        self._bind_btn = ctk.CTkButton(
            acts, text="᛭ Bind Rune", width=120, height=36, font=T.FONT_BODY,
            fg_color="#3b0764", hover_color="#7c3aed", state="disabled",
            command=self._invoke_bind_rune,
        )
        self._bind_btn.pack(side="left", padx=3)

        mid = ctk.CTkFrame(bar, fg_color="transparent")
        mid.pack(side="left", expand=True, fill="x", padx=8)
        ctk.CTkEntry(
            mid, textvariable=self._workspace, width=220, height=34,
            placeholder_text="Workspace path",
            font=T.FONT_BODY, fg_color=T.BG_CARD, border_color=T.BORDER,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            mid, text="Apply", width=64, height=34, font=T.FONT_SMALL,
            command=self._apply_workspace,
        ).pack(side="left")

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=12)
        ctk.CTkLabel(
            right, textvariable=self._selection_label,
            font=T.FONT_SMALL, text_color=T.ACCENT_HEL,
        ).pack(anchor="e")
        ctk.CTkLabel(
            right, textvariable=self._status,
            font=T.FONT_SMALL, text_color=T.ACCENT_ICE,
        ).pack(anchor="e")

    def _build_bubbles(self) -> None:
        main = ctk.CTkFrame(self, fg_color=T.BG_PANEL, corner_radius=28, border_width=1, border_color=T.BORDER)
        main.pack(fill="both", expand=True, padx=18, pady=(10, 6))

        ctk.CTkLabel(main, text="Forges of Hel", font=T.FONT_TITLE, text_color=T.TEXT_RUNE).pack(pady=(16, 2))
        ctk.CTkLabel(
            main,
            text="Tap tuners to select (glow) · 2+ unlocks Bind Rune · Dev Armory & Full Forge run instantly",
            font=T.FONT_SMALL, text_color=T.TEXT_MUTED,
        ).pack(pady=(0, 10))

        grid = ctk.CTkFrame(main, fg_color="transparent")
        grid.pack(expand=True)

        r0 = ctk.CTkFrame(grid, fg_color="transparent")
        r0.pack(pady=6)
        InstantForgeBubble(
            r0, "ᛏ", "Full Forge", "full install",
            T.ACCENT_EMBER, "#ea580c", self._full_forge,
        ).pack(side="left", padx=14)
        InstantForgeBubble(
            r0, "ᛈ", "Dev Armory", "apps & kits",
            T.ACCENT_ICE, "#0ea5e9", self._dev_armory,
        ).pack(side="left", padx=14)

        r1 = ctk.CTkFrame(grid, fg_color="transparent")
        r1.pack(pady=6)
        for fid in ("purify", "auto_mend", "cursor_bind"):
            self._add_selectable(r1, fid)

        r2 = ctk.CTkFrame(grid, fg_color="transparent")
        r2.pack(pady=6)
        for fid in ("llm_dev_mode", "quick_temper", "helheim_scan"):
            self._add_selectable(r2, fid)

        self._bind_rune_frame = ctk.CTkFrame(
            grid, fg_color="#1a0f2e", corner_radius=24,
            border_width=2, border_color="#4c1d95",
        )
        self._bind_rune_frame.pack(pady=12, padx=40, fill="x")
        self._bind_label = ctk.CTkLabel(
            self._bind_rune_frame,
            text="᛭ Bind Rune — select 2+ forges above to unlock",
            font=T.FONT_BODY, text_color=T.TEXT_MUTED,
        )
        self._bind_label.pack(pady=14)
        self._update_bind_rune_ui()

    def _add_selectable(self, row: ctk.CTkFrame, forge_id: str) -> None:
        fdef = FORGES[forge_id]
        w = SelectableForgeBubble(
            row, fdef.rune, fdef.label, fdef.sub,
            fdef.color, fdef.hover, forge_id, self._on_forge_toggle,
        )
        w.pack(side="left", padx=14)
        self._forge_widgets[forge_id] = w

    def _on_forge_toggle(self, forge_id: str, selected: bool) -> None:
        if selected:
            self._selected.add(forge_id)
        else:
            self._selected.discard(forge_id)
        self._selection_label.set(f"Selected: {len(self._selected)}")
        self._update_bind_rune_ui()
        if self._invoke_btn:
            self._invoke_btn.configure(state="normal" if self._selected else "disabled")

    def _update_bind_rune_ui(self) -> None:
        n = len(self._selected)
        if n >= 2:
            rune = bind_rune.forge_bind_rune(sorted(self._selected))
            props = " · ".join(p.name for p in rune.properties)
            self._bind_label.configure(
                text=f"᛭ {rune.name} ready — {props}",
                text_color=T.ACCENT_HEL,
            )
            if self._bind_btn:
                self._bind_btn.configure(state="normal", fg_color="#5b21b6")
        else:
            self._bind_label.configure(
                text=f"᛭ Bind Rune — select {2 - n} more forge(s)" if n == 1 else "᛭ Bind Rune — select 2+ forges to unlock",
                text_color=T.TEXT_MUTED,
            )
            if self._bind_btn:
                self._bind_btn.configure(state="disabled", fg_color="#3b0764")

    def _build_log(self) -> None:
        foot = ctk.CTkFrame(self, height=148, corner_radius=0, fg_color=T.BG_TOOLBAR)
        foot.pack(side="bottom", fill="x")
        foot.pack_propagate(False)
        ctk.CTkLabel(foot, text="Mímisbrunnr", font=T.FONT_BODY, text_color=T.TEXT_RUNE).pack(anchor="w", padx=16, pady=(8, 0))
        self._log = ctk.CTkTextbox(
            foot, height=96, font=T.FONT_LOG, fg_color=T.BG_DARK,
            text_color=T.ACCENT_ICE, corner_radius=14, border_color=T.BORDER, border_width=1,
        )
        self._log.pack(fill="both", expand=True, padx=16, pady=(2, 10))

    def log(self, msg: str) -> None:
        self._log.insert("end", msg + "\n")
        self._log.see("end")

    def status(self, msg: str) -> None:
        self._status.set(msg)

    def _log_cb(self) -> Callable[[str], None]:
        return lambda line: self.after(0, lambda l=line: self.log(l))

    def _apply_workspace(self) -> None:
        p = Path(self._workspace.get().strip()).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        self.log(f"Workspace: {p}")

    def _auto_sync(self) -> None:
        def work():
            device_sync.sync_device()
            self._sync_state = device_sync.load_sync()
            self.after(0, lambda: self.status("᛬ Synced"))
        threading.Thread(target=work, daemon=True).start()

    def _sync_device(self) -> None:
        def task(cb):
            ok, msg = device_sync.sync_device()
            self._sync_state = device_sync.load_sync()
            return ok, msg
        self._run_async("Device sync", task)

    def _show_counsel(self) -> None:
        state = self._sync_state or device_sync.load_sync() or device_sync.collect_device_state()
        recs = recommendations.build_recommendations(state)
        text = recommendations.format_recommendations_text(recs)

        win = ctk.CTkToplevel(self)
        win.title("Mímir's Counsel")
        win.geometry("520x480")
        win.configure(fg_color=T.BG_PANEL)
        win.transient(self)
        ctk.CTkLabel(win, text="Recommendations", font=T.FONT_TITLE, text_color=T.ACCENT_ICE).pack(pady=12)
        box = ctk.CTkTextbox(win, font=T.FONT_BODY, fg_color=T.BG_DARK, wrap="word")
        box.pack(fill="both", expand=True, padx=16, pady=8)
        box.insert("1.0", text)
        box.configure(state="disabled")

        def apply_top() -> None:
            if not recs:
                return
            r = recs[0]
            win.destroy()
            if r.kind == "forge" and r.action in FORGES:
                self._forge_widgets[r.action].set_selected(True)
                self._on_forge_toggle(r.action, True)
            elif r.action == "full_forge":
                self._full_forge()
            elif r.action == "bind_rune" and len(self._selected) < 2:
                messagebox.showinfo(T.APP_NAME, "Select 2+ forges, then Bind Rune.")

        ctk.CTkButton(
            win, text="Apply top suggestion", fg_color="#166534",
            command=apply_top,
        ).pack(pady=8)
        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=(0, 12))

    def _invoke_selected(self) -> None:
        if not self._selected:
            return
        ids = sorted(self._selected)
        self._run_async("Invoke selected", lambda cb: bind_rune.run_selected_forges(ids, cb))

    def _invoke_bind_rune(self) -> None:
        if len(self._selected) < 2:
            messagebox.showinfo(T.APP_NAME, "Select at least 2 forges to bind a rune.")
            return
        ids = sorted(self._selected)
        self._run_async("Bind Rune", lambda cb: bind_rune.invoke_bind_rune(ids, cb))

    def _run_async(self, name: str, task: Callable[[Callable[[str], None]], tuple[bool, str]]) -> None:
        if self._busy:
            messagebox.showwarning(T.APP_NAME, "A forge is already running.")
            return

        def worker() -> None:
            self._busy = True
            self.after(0, lambda: self.status(f"᛬ {name}…"))
            self.after(0, lambda: self.log(f"── {name} ──"))
            try:
                ok, msg = task(self._log_cb())
                self.after(0, lambda: self.log(msg))
                self.after(0, lambda: self.status("᛬ Done" if ok else "᛬ Check log"))
                if ok:
                    self.after(0, lambda: messagebox.showinfo(T.APP_NAME, msg[:700]))
                else:
                    self.after(0, lambda: messagebox.showerror(T.APP_NAME, msg[:700]))
                self.after(0, self._refresh_sync)
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror(T.APP_NAME, str(exc)))
            finally:
                self.after(0, lambda: setattr(self, "_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_sync(self) -> None:
        self._sync_state = device_sync.load_sync()

    def _full_forge(self) -> None:
        if not INSTALL_SCRIPT.exists():
            messagebox.showerror(T.APP_NAME, f"Missing:\n{INSTALL_SCRIPT}")
            return
        self._run_async("Full Forge", lambda cb: (
            pkexec_run(str(INSTALL_SCRIPT), cb) == 0,
            f"See {REPORT}",
        ))

    def _dev_armory(self) -> None:
        self._open_armory()

    def _open_armory(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Dev Armory")
        win.geometry("640x620")
        win.configure(fg_color=T.BG_PANEL)
        win.transient(self)
        ctk.CTkLabel(
            win, text="⚒ Dev Armory — separate from bind runes",
            font=T.FONT_TITLE, text_color=T.ACCENT_ICE,
        ).pack(pady=14)
        scroll = ctk.CTkScrollableFrame(win, fg_color=T.BG_PANEL)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        rec = ctk.CTkFrame(scroll, fg_color="#0f2a22", corner_radius=16, border_color=T.ACCENT_HEL, border_width=1)
        rec.pack(fill="x", pady=8)
        rt = ctk.CTkFrame(rec, fg_color="transparent")
        rt.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(rt, text="Recommended field kit", font=T.FONT_TITLE, text_color=T.ACCENT_HEL).pack(side="left", expand=True, anchor="w")

        def kit() -> None:
            win.destroy()
            self._run_async("Recommended kit", lambda cb: stack_tune.install_recommended_kit(cb))

        ctk.CTkButton(rt, text="Install all", fg_color="#166534", command=kit).pack(side="right")

        state = self._sync_state or {}
        recs = [r for r in recommendations.build_recommendations(state) if r.kind == "armory"][:4]
        if recs:
            ctk.CTkLabel(scroll, text="᛬ Sync suggests:", font=T.FONT_SMALL, text_color=T.ACCENT_RUNE).pack(anchor="w", pady=(8, 4))
            for r in recs:
                ctk.CTkLabel(scroll, text=f"• {r.title} — {r.reason}", font=T.FONT_SMALL, text_color=T.TEXT_MUTED, anchor="w").pack(fill="x")

        for section, pids in dev_tools.DEV_SECTIONS:
            ctk.CTkLabel(scroll, text=section, font=T.FONT_TITLE, text_color=T.ACCENT_RUNE).pack(anchor="w", pady=(12, 4))
            for pid in pids:
                prof = dev_tools.DEV_PROFILES.get(pid)
                if prof:
                    self._armory_card(scroll, win, pid, prof)
        ctk.CTkButton(win, text="Close", command=win.destroy).pack(pady=10)

    def _armory_card(self, parent, win: ctk.CTkToplevel, pid: str, prof: dict) -> None:
        card = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=14, border_width=1, border_color=T.BORDER)
        card.pack(fill="x", pady=6)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(top, text=prof["label"], font=T.FONT_BODY).pack(side="left", expand=True, anchor="w")

        def go(p=pid, t=prof["label"]) -> None:
            win.destroy()
            self._run_async(t, lambda cb: dev_tools.install_profile(p, cb))

        ctk.CTkButton(top, text="Install", width=90, fg_color="#166534", command=go).pack(side="right")
        ctk.CTkLabel(card, text=prof.get("desc", ""), font=T.FONT_SMALL, text_color=T.TEXT_MUTED).pack(
            padx=14, anchor="w", pady=(0, 10),
        )


def main() -> None:
    HelgrindApp().mainloop()


if __name__ == "__main__":
    main()
