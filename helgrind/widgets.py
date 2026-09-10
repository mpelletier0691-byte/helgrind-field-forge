"""Helgrind UI widgets."""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from helgrind import theme as T


class SelectableForgeBubble(ctk.CTkFrame):
    """Tap to select (highlight); does not run until Invoke / Bind."""

    def __init__(
        self,
        master,
        rune: str,
        label: str,
        sub: str,
        color: str,
        hover: str,
        forge_id: str,
        on_toggle: Callable[[str, bool], None],
        size: int = T.BUBBLE_SIZE,
    ) -> None:
        super().__init__(
            master, fg_color="transparent",
            width=T.BUBBLE_RING + 8, height=T.BUBBLE_RING + 12,
        )
        self.pack_propagate(False)
        self.forge_id = forge_id
        self._color = color
        self._hover = hover
        self._on_toggle = on_toggle
        self._selected = False

        self._ring = ctk.CTkFrame(
            self, width=T.BUBBLE_RING + 6, height=T.BUBBLE_RING + 6,
            corner_radius=(T.BUBBLE_RING + 6) // 2,
            fg_color="transparent", border_width=0,
        )
        self._ring.place(relx=0.5, rely=0.4, anchor="center")

        self._btn = ctk.CTkButton(
            self._ring,
            text=f"{rune}\n{label}",
            width=size, height=size,
            corner_radius=size // 2,
            fg_color=color, hover_color=hover,
            text_color=T.TEXT_PRIMARY, font=T.FONT_BUBBLE,
            command=self._toggle,
        )
        self._btn.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self, text=sub, font=T.FONT_SMALL, text_color=T.TEXT_MUTED,
        ).place(relx=0.5, rely=0.9, anchor="center")

    def _toggle(self) -> None:
        self.set_selected(not self._selected)

    def set_selected(self, on: bool) -> None:
        self._selected = on
        if on:
            self._ring.configure(border_width=4, border_color=T.ACCENT_HEL)
            self._btn.configure(border_width=2, border_color="#ecfdf5")
        else:
            self._ring.configure(border_width=0)
            self._btn.configure(border_width=0)
        self._on_toggle(self.forge_id, on)


class InstantForgeBubble(ctk.CTkFrame):
    """Runs immediately on click (Full Forge style)."""

    def __init__(
        self, master, rune: str, label: str, sub: str,
        color: str, hover: str, command: Callable[[], None],
        size: int = T.BUBBLE_SIZE,
    ) -> None:
        super().__init__(master, fg_color="transparent", width=T.BUBBLE_RING, height=T.BUBBLE_RING)
        self.pack_propagate(False)
        ctk.CTkButton(
            self, text=f"{rune}\n{label}",
            width=size, height=size, corner_radius=size // 2,
            fg_color=color, hover_color=hover,
            text_color=T.TEXT_PRIMARY, font=T.FONT_BUBBLE, command=command,
        ).place(relx=0.5, rely=0.42, anchor="center")
        ctk.CTkLabel(
            self, text=sub, font=T.FONT_SMALL, text_color=T.TEXT_MUTED,
        ).place(relx=0.5, rely=0.88, anchor="center")
