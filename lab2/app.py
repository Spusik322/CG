import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from utils import cv2_imread_unicode, to_gray, ensure_rgb
from contrast import process_contrast
from filters import process_highpass

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лаб. работа 2 | Вариант 3")
        self.root.geometry("1100x800")
        
        self.img_orig = None
        
        self.examples = {
            "Капитолий (серое)": "images/capitol.png",
            "Семена (серое)": "images/seeds.png",
            "Луна (серое)": "images/moon.png",
            "Цветное малоконтрастное": "images/color_low.png",
            "Цветное с тенью": "images/color_uneven.png",
            "Цветное насыщенное": "images/color_vivid.png"
        }
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="1. Гистограмма и контраст")
        self.notebook.add(self.tab2, text="2. Высокочастотные фильтры")
        
        self.setup_tab1()
        self.setup_tab2()

    def setup_tab1(self):
        ctrl_frame = ttk.Frame(self.tab1)
        ctrl_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        ttk.Button(ctrl_frame, text="Загрузить из файла", command=self.load_image).pack(fill='x', pady=2)
        
        ttk.Label(ctrl_frame, text="Или выберите пример:").pack(anchor='w', pady=(5,0))
        self.combo_ex_1 = ttk.Combobox(ctrl_frame, values=list(self.examples.keys()), state="readonly")
        self.combo_ex_1.pack(fill='x', pady=2)
        self.combo_ex_1.bind("<<ComboboxSelected>>", self.load_example)
        
        ttk.Label(ctrl_frame, text="Метод:").pack(anchor='w', pady=(10,0))
        self.method_1 = ttk.Combobox(ctrl_frame, values=[
            "Линейное (серый)", "Эквализация (серый)",
            "Линейное RGB (цвет)", "Линейное HSV (цвет)",
            "Эквализация RGB (цвет)", "Эквализация HSV (цвет)"
        ], state="readonly")
        self.method_1.current(0)
        self.method_1.pack(fill='x', pady=5)
        
        ttk.Label(ctrl_frame, text="Нижний %:").pack(anchor='w')
        self.slider_low = tk.Scale(ctrl_frame, from_=0, to=50, orient='horizontal', resolution=0.5)
        self.slider_low.set(1)
        self.slider_low.pack(fill='x')
        
        ttk.Label(ctrl_frame, text="Верхний %:").pack(anchor='w')
        self.slider_high = tk.Scale(ctrl_frame, from_=50, to=100, orient='horizontal', resolution=0.5)
        self.slider_high.set(99)
        self.slider_high.pack(fill='x')
        
        ttk.Button(ctrl_frame, text="Применить", command=self.apply_contrast).pack(fill='x', pady=15)
        
        self.stats_1 = tk.Text(ctrl_frame, width=35, height=15, font=("Courier", 9))
        self.stats_1.pack(fill='x', pady=5)
        
        view_frame = ttk.Frame(self.tab1)
        view_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.lbl_orig_1 = ttk.Label(view_frame, text="Оригинал", relief="solid", anchor='center')
        self.lbl_orig_1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.lbl_res_1 = ttk.Label(view_frame, text="Результат", relief="solid", anchor='center')
        self.lbl_res_1.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.fig_1, (self.ax_h1, self.ax_h2) = plt.subplots(1, 2, figsize=(6, 2.5), dpi=100)
        self.canvas_1 = FigureCanvasTkAgg(self.fig_1, master=view_frame)
        self.canvas_1.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        view_frame.rowconfigure(0, weight=1)
        view_frame.columnconfigure(0, weight=1)
        view_frame.columnconfigure(1, weight=1)

    def setup_tab2(self):
        ctrl_frame = ttk.Frame(self.tab2)
        ctrl_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        ttk.Button(ctrl_frame, text="Загрузить из файла", command=self.load_image).pack(fill='x', pady=2)
        
        ttk.Label(ctrl_frame, text="Или выберите пример:").pack(anchor='w', pady=(5,0))
        self.combo_ex_2 = ttk.Combobox(ctrl_frame, values=list(self.examples.keys()), state="readonly")
        self.combo_ex_2.pack(fill='x', pady=2)
        self.combo_ex_2.bind("<<ComboboxSelected>>", self.load_example)
        
        ttk.Label(ctrl_frame, text="Фильтр:").pack(anchor='w', pady=(10,0))
        self.method_2 = ttk.Combobox(ctrl_frame, values=[
            "Лапласиан", "Unsharp Masking", "LoG (Лапласиан гауссиана)"
        ], state="readonly")
        self.method_2.current(0)
        self.method_2.pack(fill='x', pady=5)
        
        ttk.Label(ctrl_frame, text="Сила (amount):").pack(anchor='w')
        self.slider_amount = tk.Scale(ctrl_frame, from_=0.0, to=3.0, orient='horizontal', resolution=0.1)
        self.slider_amount.set(1.0)
        self.slider_amount.pack(fill='x')
        
        ttk.Label(ctrl_frame, text="Sigma:").pack(anchor='w')
        self.slider_sigma = tk.Scale(ctrl_frame, from_=0.1, to=5.0, orient='horizontal', resolution=0.1)
        self.slider_sigma.set(1.0)
        self.slider_sigma.pack(fill='x')
        
        ttk.Button(ctrl_frame, text="Применить", command=self.apply_filter).pack(fill='x', pady=15)
        
        self.stats_2 = tk.Text(ctrl_frame, width=35, height=15, font=("Courier", 9))
        self.stats_2.pack(fill='x', pady=5)
        
        view_frame = ttk.Frame(self.tab2)
        view_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.lbl_orig_2 = ttk.Label(view_frame, text="Оригинал", relief="solid", anchor='center')
        self.lbl_orig_2.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.lbl_res_2 = ttk.Label(view_frame, text="Результат", relief="solid", anchor='center')
        self.lbl_res_2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.fig_2, (self.ax_h3, self.ax_h4) = plt.subplots(1, 2, figsize=(6, 2.5), dpi=100)
        self.canvas_2 = FigureCanvasTkAgg(self.fig_2, master=view_frame)
        self.canvas_2.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        view_frame.rowconfigure(0, weight=1)
        view_frame.columnconfigure(0, weight=1)
        view_frame.columnconfigure(1, weight=1)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif")])
        if not path: return
        self._process_loaded_image(path)

    def load_example(self, event):
        selected_name = event.widget.get()
        path = self.examples.get(selected_name)
        if path and os.path.exists(path):
            self._process_loaded_image(path)
        else:
            self.stats_1.delete(1.0, tk.END)
            self.stats_1.insert(tk.END, f"Файл не найден:\n{path}")
            self.stats_2.delete(1.0, tk.END)
            self.stats_2.insert(tk.END, f"Файл не найден:\n{path}")

    def _process_loaded_image(self, path):
        self.img_orig = cv2_imread_unicode(path)
        if self.img_orig is None:
            return
            
        self.display_image(self.img_orig, self.lbl_orig_1)
        self.display_image(self.img_orig, self.lbl_orig_2)
        
        self.lbl_res_1.config(image='', text="Результат")
        self.lbl_res_2.config(image='', text="Результат")
        self.stats_1.delete(1.0, tk.END)
        self.stats_2.delete(1.0, tk.END)
        
        self.plot_histogram(self.ax_h1, self.img_orig, "ДО")
        self.plot_histogram(self.ax_h2, self.img_orig, "ПОСЛЕ")
        self.canvas_1.draw()
        
        self.plot_histogram(self.ax_h3, self.img_orig, "ДО")
        self.plot_histogram(self.ax_h4, self.img_orig, "ПОСЛЕ")
        self.canvas_2.draw()

    def apply_contrast(self):
        if self.img_orig is None: return
        method = self.method_1.get()
        low = self.slider_low.get()
        high = self.slider_high.get()
        
        res, stats = process_contrast(self.img_orig, method, low, high)
        if res is not None:
            self.display_image(res, self.lbl_res_1)
            self.plot_histogram(self.ax_h2, res, "ПОСЛЕ")
            self.canvas_1.draw()
            
            self.stats_1.delete(1.0, tk.END)
            self.stats_1.insert(tk.END, stats)

    def apply_filter(self):
        if self.img_orig is None: return
        method = self.method_2.get()
        amount = self.slider_amount.get()
        sigma = self.slider_sigma.get()
        
        res, stats = process_highpass(self.img_orig, method, amount, sigma)
        if res is not None:
            self.display_image(res, self.lbl_res_2)
            self.plot_histogram(self.ax_h4, res, "ПОСЛЕ")
            self.canvas_2.draw()
            
            self.stats_2.delete(1.0, tk.END)
            self.stats_2.insert(tk.END, stats)

    def display_image(self, img_arr, label_widget):
        img_pil = Image.fromarray(img_arr)
        img_pil.thumbnail((350, 350))
        img_tk = ImageTk.PhotoImage(img_pil)
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk

    def plot_histogram(self, ax, img_arr, title):
        ax.clear()
        gray = to_gray(ensure_rgb(img_arr))
        ax.hist(gray.ravel(), bins=256, range=(0, 256), color="black")
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 256)
        ax.set_yticks([])
        ax.tick_params(axis='x', labelsize=8)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()