import tkinter as tk
from tkinter import ttk

from utils import clamp, format_number


class ColorRow(ttk.Frame):
    def __init__(self, parent, app, model, comp, low, high):
        super().__init__(parent)

        self.app = app
        self.model = model
        self.comp = comp
        self.low = low
        self.high = high

        self.columnconfigure(1, weight=1)

        ttk.Label(
            self,
            text=comp,
            width=3
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.scale = ttk.Scale(
            self,
            from_=low,
            to=high,
            orient=tk.HORIZONTAL,
            command=self._on_scale_change
        )
        self.scale.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 6)
        )

        self.entry = ttk.Entry(self, width=8)
        self.entry.grid(
            row=0,
            column=2
        )

        self.entry.bind("<Return>", self._on_entry_change)
        self.entry.bind("<FocusOut>", self._on_entry_change)

        self.set(0)

    def _on_scale_change(self, value):
        self.app.on_scale_change(self.model, self.comp, value)

    def _on_entry_change(self, event=None):
        self.app.on_entry_change(self.model, self.comp)

    def set(self, value):
        value = clamp(float(value), self.low, self.high)

        if abs(value - round(value)) < 1e-6:
            value = float(round(value))

        self.scale.set(value)

        self.entry.delete(0, tk.END)
        self.entry.insert(0, format_number(value))