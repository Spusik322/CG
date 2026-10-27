import tkinter as tk
from tkinter import messagebox
import algorithms
import math
import time

class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 3: Базовые растровые алгоритмы")
        self.root.geometry("950x700")
        
        self.canvas_width = 650
        self.canvas_height = 650
        self.base_grid_step = 20
        
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.last_x = 0
        self.last_y = 0
        
        self.current_points = []
        
        self.setup_ui()
        self.bind_events()
        self.redraw_canvas()
        
    def setup_ui(self):
        control_frame = tk.Frame(self.root, width=280, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(control_frame, text="1. Выберите алгоритм:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        
        self.algo_var = tk.StringVar(value="bresenham_line")
        algos = [
            ("Пошаговый алгоритм", "step"),
            ("Алгоритм ЦДА", "dda"),
            ("Брезенхем (линия)", "bresenham_line"),
            ("Брезенхем (окружность)", "bresenham_circle")
        ]
        for text, val in algos:
            tk.Radiobutton(control_frame, text=text, variable=self.algo_var, value=val).pack(anchor="w")
            
        tk.Label(control_frame, text="\n2. Введите координаты:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        self.x2_var = tk.StringVar(value="10")
        self.y2_var = tk.StringVar(value="5")
        
        self.create_input(control_frame, "X1 / X центра:", self.x1_var)
        self.create_input(control_frame, "Y1 / Y центра:", self.y1_var)
        self.create_input(control_frame, "X2 / Радиус:", self.x2_var)
        self.create_input(control_frame, "Y2 / (для круга игнор):", self.y2_var)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(pady=15, fill=tk.X)
        
        tk.Button(btn_frame, text="Нарисовать", command=self.draw, font=("Arial", 10, "bold"), pady=5).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        tk.Button(btn_frame, text="Очистить", command=self.clear, font=("Arial", 10), pady=5).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5,0))
        
        tk.Label(control_frame, text="3. Статистика и сравнение:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.stats_text = tk.Text(control_frame, height=10, width=35, font=("Consolas", 9), bg="#f0f0f0", state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X)
        
        tk.Label(control_frame, text="Управление:\nМасштаб - Колесико мыши\nПеремещение - Зажать ЛКМ", 
                 font=("Arial", 8), fg="gray", justify=tk.LEFT).pack(side=tk.BOTTOM, anchor="w", pady=10)

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", cursor="crosshair")
        self.canvas.pack(padx=10, pady=10)

    def create_input(self, parent, label_text, var):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label_text, width=18, anchor="w").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=var, width=6).pack(side=tk.RIGHT)

    def bind_events(self):
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)

    def on_zoom(self, event):
        zoom_factor = 1.2 if (event.num == 4 or event.delta > 0) else 1/1.2
        
        cx = self.canvas_width // 2 + self.offset_x
        cy = self.canvas_height // 2 + self.offset_y
        pixel_step = self.base_grid_step * self.zoom
        
        math_x = (event.x - cx) / pixel_step
        math_y = (cy - event.y) / pixel_step
        
        self.zoom *= zoom_factor
        self.zoom = max(0.1, min(self.zoom, 10.0))
        
        new_pixel_step = self.base_grid_step * self.zoom
        self.offset_x = event.x - math_x * new_pixel_step - self.canvas_width // 2
        self.offset_y = event.y + math_y * new_pixel_step - self.canvas_height // 2
        
        self.redraw_canvas()

    def on_pan_start(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def on_pan_move(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.offset_x += dx
        self.offset_y += dy
        self.last_x = event.x
        self.last_y = event.y
        self.redraw_canvas()

    def get_grid_step(self):
        pixel_step = self.base_grid_step * self.zoom
        target = 30.0
        if pixel_step >= target:
            return 1
        
        k = 1
        while pixel_step * k < target:
            if str(k).startswith('1'): k *= 5
            elif str(k).startswith('5'): k *= 2
        return k

    def redraw_canvas(self):
        self.canvas.delete("all")
        step = self.get_grid_step()
        cx = self.canvas_width // 2 + self.offset_x
        cy = self.canvas_height // 2 + self.offset_y
        pixel_step = self.base_grid_step * self.zoom
        
        min_x = math.floor(-cx / pixel_step)
        max_x = math.ceil((self.canvas_width - cx) / pixel_step)
        min_y = math.floor((cy - self.canvas_height) / pixel_step)
        max_y = math.ceil(cy / pixel_step)
        
        start_x = math.floor(min_x / step) * step
        end_x = math.ceil(max_x / step) * step
        
        for i in range(start_x, end_x + 1, step):
            sx = cx + (i + 0.5) * pixel_step
            if 0 <= sx <= self.canvas_width:
                self.canvas.create_line(sx, 0, sx, self.canvas_height, fill="#e0e0e0")
            
            lx = cx + i * pixel_step
            if 0 <= lx <= self.canvas_width and i != 0:
                self.canvas.create_text(lx, cy + 10, text=str(i), font=("Arial", 8), fill="gray")
                
        start_y = math.floor(min_y / step) * step
        end_y = math.ceil(max_y / step) * step
        
        for j in range(start_y, end_y + 1, step):
            sy = cy - (j + 0.5) * pixel_step
            if 0 <= sy <= self.canvas_height:
                self.canvas.create_line(0, sy, self.canvas_width, sy, fill="#e0e0e0")
            
            ly = cy - j * pixel_step
            if 0 <= ly <= self.canvas_height and j != 0:
                self.canvas.create_text(cx - 10, ly, text=str(j), font=("Arial", 8), fill="gray")
        
        self.canvas.create_line(0, cy, self.canvas_width, cy, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_line(cx, self.canvas_height, cx, 0, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_text(self.canvas_width - 15, cy - 15, text="X", font=("Arial", 12, "bold"))
        self.canvas.create_text(cx + 15, 15, text="Y", font=("Arial", 12, "bold"))
        self.canvas.create_text(cx - 10, cy + 10, text="0", font=("Arial", 9))

        if hasattr(self, 'current_points') and self.current_points:
            for px, py in self.current_points:
                sx = cx + px * pixel_step
                sy = cy - py * pixel_step
                
                r = pixel_step / 2
                self.canvas.create_rectangle(sx - r, sy - r, sx + r, sy + r, fill="red", outline="darkred")

    def clear(self):
        self.current_points = []
        self.redraw_canvas()
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)

    def draw(self):
        try:
            x1, y1, x2, y2 = int(self.x1_var.get()), int(self.y1_var.get()), int(self.x2_var.get()), int(self.y2_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа!")
            return
            
        algo = self.algo_var.get()
        algo_name = ""
        runs = 1000
        points = []
        
        start_time = time.perf_counter()
        for _ in range(runs):
            if algo == "step":
                points, _ = algorithms.step_by_step(x1, y1, x2, y2)
            elif algo == "dda":
                points, _ = algorithms.dda(x1, y1, x2, y2)
            elif algo == "bresenham_line":
                points, _ = algorithms.bresenham_line(x1, y1, x2, y2)
            elif algo == "bresenham_circle":
                points, _ = algorithms.bresenham_circle(x1, y1, x2)
        end_time = time.perf_counter()
        
        avg_time_ms = ((end_time - start_time) * 1000) / runs
        
        if algo == "step": algo_name = "Пошаговый"
        elif algo == "dda": algo_name = "ЦДА (DDA)"
        elif algo == "bresenham_line": algo_name = "Брезенхем (линия)"
        elif algo == "bresenham_circle": algo_name = "Брезенхем (окружность)"
            
        self.current_points = points
        self.redraw_canvas()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        stats = (f"РЕЗУЛЬТАТЫ\n"
                 f"Алгоритм: {algo_name}\n"
                 f"Среднее время ({runs} запусков):\n{avg_time_ms:.6f} мс\n"
                 f"Кол-во точек: {len(self.current_points)}\n")
        
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()