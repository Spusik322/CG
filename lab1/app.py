import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

from config import MODEL_DEFS, create_empty_state
from utils import clamp
from conversions import (
    rgb_to_cmyk,
    cmyk_to_rgb,
    rgb_to_hls,
    hls_to_rgb,
)
from widgets import ColorRow


class ColorLabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CMYK - RGB - HLS")
        self.root.geometry("1100x430")
        self.root.minsize(980, 380)

        self.rgb = (255, 0, 0)
        self.values = create_empty_state()
        self.rows = {}
        self.updating = True
        self.manual_model = None

        self._build_ui()

        self.updating = False
        self.refresh_all()

    def _build_ui(self):
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill=tk.X)

        ttk.Button(
            controls,
            text="Выбрать цвет из палитры",
            command=self.pick_color
        ).pack(side=tk.LEFT)

        ttk.Label(controls, text=" Hex:").pack(side=tk.LEFT, padx=(12, 4))

        self.hex_entry = ttk.Entry(controls, width=10)
        self.hex_entry.pack(side=tk.LEFT)
        self.hex_entry.bind("<Return>", self.apply_hex)

        ttk.Button(
            controls,
            text="Применить цвет",
            command=self.apply_hex
        ).pack(side=tk.LEFT, padx=4)

        self.preview = tk.Label(
            controls,
            width=18,
            relief="ridge",
            bd=2,
            bg="#ff0000"
        )
        self.preview.pack(side=tk.LEFT, padx=8)

        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        for i in range(3):
            main.columnconfigure(i, weight=1)

        self._build_model_frame(main, "CMYK", 0, 0)
        self._build_model_frame(main, "RGB", 0, 1)
        self._build_model_frame(main, "HLS", 0, 2)

    def _build_model_frame(self, parent, model, row, col):
        frame = ttk.LabelFrame(parent, text=model, padding=6)
        frame.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=5
        )

        frame.columnconfigure(0, weight=1)

        for i, (comp, low, high) in enumerate(MODEL_DEFS[model]):
            widget = ColorRow(frame, self, model, comp, low, high)
            widget.grid(
                row=i,
                column=0,
                sticky="ew",
                pady=2
            )
            self.rows[(model, comp)] = widget

    def pick_color(self):
        color, hex_color = colorchooser.askcolor(title="Выберите цвет")

        if color is None:
            return

        r, g, b = color

        self.rgb = (
            int(round(clamp(r, 0, 255))),
            int(round(clamp(g, 0, 255))),
            int(round(clamp(b, 0, 255)))
        )

        self.manual_model = None
        self.refresh_all()

    def apply_hex(self, event=None):
        text = self.hex_entry.get().strip().lstrip("#")

        if len(text) == 3:
            text = "".join(ch * 2 for ch in text)

        if len(text) != 6:
            messagebox.showerror(
                "Ошибка",
                "Введите цвет в формате #RRGGBB или #RGB."
            )
            self.refresh_all()
            return

        try:
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Hex-цвет должен содержать шестнадцатеричные цифры 0-9, A-F."
            )
            self.refresh_all()
            return

        self.rgb = (r, g, b)
        self.manual_model = None
        self.refresh_all()

    def on_scale_change(self, model, comp, value):
        if self.updating:
            return

        try:
            value = float(value)
        except ValueError:
            return

        self._set_component(model, comp, value)

    def on_entry_change(self, model, comp):
        if self.updating:
            return

        row = self.rows.get((model, comp))
        if row is None:
            return

        text = row.entry.get().strip().replace(",", ".")

        if not text:
            old_updating = self.updating
            self.updating = True
            row.set(self.values[model][comp])
            self.updating = old_updating
            return

        try:
            value = float(text)
        except ValueError:
            old_updating = self.updating
            self.updating = True
            row.set(self.values[model][comp])
            self.updating = old_updating
            return

        self._set_component(model, comp, value)

    def _set_component(self, model, comp, value):
        row = self.rows.get((model, comp))
        if row is None:
            return

        value = clamp(value, row.low, row.high)

        self.manual_model = model
        self.values[model][comp] = value

        self._update_rgb_from_model(model)
        self.refresh_all()

    def _update_rgb_from_model(self, model):
        vals = self.values[model]

        if model == "RGB":
            r = int(round(clamp(vals["R"], 0, 255)))
            g = int(round(clamp(vals["G"], 0, 255)))
            b = int(round(clamp(vals["B"], 0, 255)))
            self.rgb = (r, g, b)

        elif model == "CMYK":
            self.rgb = cmyk_to_rgb(
                vals["C"],
                vals["M"],
                vals["Y"],
                vals["K"]
            )

        elif model == "HLS":
            self.rgb = hls_to_rgb(
                vals["H"],
                vals["L"],
                vals["S"]
            )

    def refresh_all(self):
        self.updating = True

        r, g, b = self.rgb

        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        self.preview.configure(bg=hex_color)

        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, hex_color)

        computed = create_empty_state()

        computed["RGB"] = {
            "R": float(r),
            "G": float(g),
            "B": float(b)
        }

        c, m, y, k = rgb_to_cmyk(r, g, b)
        computed["CMYK"] = {
            "C": c,
            "M": m,
            "Y": y,
            "K": k
        }

        h, l, s = rgb_to_hls(r, g, b)
        computed["HLS"] = {
            "H": h,
            "L": l,
            "S": s
        }

        for model in MODEL_DEFS:
            if model == self.manual_model and model != "RGB":
                if model not in self.values:
                    self.values[model] = computed[model]
            else:
                self.values[model] = computed[model]

        for model, comps in self.values.items():
            for comp, value in comps.items():
                row = self.rows.get((model, comp))
                if row is not None:
                    row.set(value)

        self.updating = False

    def run(self):
        self.root.mainloop()