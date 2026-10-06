import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

from config import MODEL_DEFS, create_empty_state
from utils import clamp
from conversions import (
    rgb_to_cmyk,
    cmyk_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_hls,
    hls_to_rgb,
)
from widgets import ColorRow


class ColorLabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лабораторная работа 1: цветовые модели")
        self.root.geometry("1100x480")
        self.root.minsize(980, 400)

        self.rgb = (255, 0, 0)
        self.values = create_empty_state()
        self.draft_values = create_empty_state()
        self.rows = {}
        self.updating = True
        self.active_model = None
        self.manual_model = None
        self.variant = tk.StringVar(value="HSV")

        self._build_ui()

        self.updating = False
        self.refresh_all()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Вариант:").pack(side=tk.LEFT)

        ttk.Radiobutton(
            top,
            text="Чётный: CMYK – RGB – HSV",
            variable=self.variant,
            value="HSV",
            command=self._rebuild_third
        ).pack(side=tk.LEFT, padx=6)

        ttk.Radiobutton(
            top,
            text="Нечётный: CMYK – RGB – HLS",
            variable=self.variant,
            value="HLS",
            command=self._rebuild_third
        ).pack(side=tk.LEFT, padx=6)

        ttk.Label(
            top,
            text="Изменения применяются только кнопкой «Применить» у модели.",
            foreground="#444"
        ).pack(side=tk.LEFT, padx=12)

        controls = ttk.Frame(self.root, padding=(8, 0, 8, 8))
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

        self.third_container = ttk.Frame(main)
        self.third_container.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=(5, 0)
        )

        self._rebuild_third(refresh=False)

    def _build_model_frame(self, parent, model, row, col):
        frame = ttk.LabelFrame(parent, text=model, padding=6)
        frame.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=5
        )
        self._fill_model_frame(frame, model)

    def _fill_model_frame(self, frame, model):
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

        apply_button = ttk.Button(
            frame,
            text=f"Применить {model}",
            command=lambda m=model: self.apply_model(m)
        )
        apply_button.grid(
            row=len(MODEL_DEFS[model]),
            column=0,
            sticky="ew",
            pady=(6, 0)
        )

    def _rebuild_third(self, refresh=True):
        self.updating = True

        if getattr(self, "active_model", None) is not None:
            self.restore_model(self.active_model)

        for child in self.third_container.winfo_children():
            child.destroy()

        for key in list(self.rows.keys()):
            if key[0] in ("HSV", "HLS"):
                del self.rows[key]

        model = self.variant.get()

        frame = ttk.LabelFrame(self.third_container, text=model, padding=6)
        frame.pack(fill=tk.BOTH, expand=True)

        self._fill_model_frame(frame, model)

        self.updating = False

        if refresh:
            self.refresh_all()

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

        self._begin_edit(model)
        self._set_draft_component(model, comp, value)

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
            row.set(self.draft_values[model][comp])
            self.updating = old_updating
            return

        try:
            value = float(text)
        except ValueError:
            old_updating = self.updating
            self.updating = True
            row.set(self.draft_values[model][comp])
            self.updating = old_updating
            return

        self._begin_edit(model)
        self._set_draft_component(model, comp, value)

    def _begin_edit(self, model):
        if self.active_model is not None and self.active_model != model:
            self.restore_model(self.active_model)

        self.active_model = model

    def _set_draft_component(self, model, comp, value):
        row = self.rows.get((model, comp))
        if row is None:
            return

        value = clamp(value, row.low, row.high)
        self.draft_values[model][comp] = value

        old_updating = self.updating
        self.updating = True
        row.set(value)
        self.updating = old_updating

    def apply_model(self, model):
        if model not in self.draft_values:
            return

        if self.active_model is not None and self.active_model != model:
            self.restore_model(self.active_model)

        self.values[model] = self.draft_values[model].copy()
        self._update_rgb_from_model(model)

        if model == "RGB":
            self.values["RGB"] = {
                "R": float(self.rgb[0]),
                "G": float(self.rgb[1]),
                "B": float(self.rgb[2]),
            }
            self.manual_model = None
        else:
            self.manual_model = model

        self.active_model = None
        self.refresh_all()

    def restore_model(self, model):
        if model is None or model not in self.values:
            return

        old_updating = self.updating
        self.updating = True

        for comp, value in self.values[model].items():
            row = self.rows.get((model, comp))
            if row is not None:
                row.set(value)

        self.updating = old_updating

        self.draft_values[model] = self.values[model].copy()

        if self.active_model == model:
            self.active_model = None

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

        elif model == "HSV":
            self.rgb = hsv_to_rgb(
                vals["H"],
                vals["S"],
                vals["V"]
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

        h, s, v = rgb_to_hsv(r, g, b)
        computed["HSV"] = {
            "H": h,
            "S": s,
            "V": v
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

        self.draft_values = {
            model: comps.copy()
            for model, comps in self.values.items()
        }

        self.active_model = None

        for model, comps in self.values.items():
            for comp, value in comps.items():
                row = self.rows.get((model, comp))
                if row is not None:
                    row.set(value)

        self.updating = False

    def run(self):
        self.root.mainloop()