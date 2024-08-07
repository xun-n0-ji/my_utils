import tkinter as tk
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk, ImageOps
import numpy as np
import pandas as pd

class ToneCurveApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Image Display")
        
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()
        
        self.image = Image.open(image_path).convert("L")
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        self.gamma_button = tk.Button(root, text="gamma", command=self.open_tone_curve_window)
        self.gamma_button.pack()

    def open_tone_curve_window(self):
        ToneCurveWindow(self.image, self)

    def update_image(self, new_image):
        self.photo = ImageTk.PhotoImage(new_image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

class ToneCurveWindow:
    def __init__(self, image, main_app):
        self.window = Toplevel()
        self.window.title("Tone Curve Adjustment")
        
        self.canvas = tk.Canvas(self.window, width=500, height=500, bg='#2e2e2e')
        self.canvas.pack()
        
        self.image = image
        self.main_app = main_app
        self.points = []
        self.vertical_lines = []
        self.regions = []
        self.selected_point = None
        
        for i in range(25):
            x = 20 * i
            point = self.canvas.create_oval(x - 5, 480, x + 5, 490, fill="white", tags=f"point{i}")
            self.points.append(point)
            v_line = self.canvas.create_line(x, 0, x, 500, fill="#696969")
            self.vertical_lines.append(v_line)
            if i > 0:
                self.regions.append(self.canvas.create_rectangle((x-20, 0, x, 500), outline="", tags=f"region{i-1}"))
        
        self.lines = []
        self.update_lines()

        for point in self.points:
            self.canvas.tag_bind(point, "<ButtonPress-1>", self.on_button_press)
            self.canvas.tag_bind(point, "<B1-Motion>", self.on_motion)

        for region in self.regions:
            self.canvas.tag_bind(region, "<ButtonPress-1>", self.on_region_press)
            self.canvas.tag_bind(region, "<B1-Motion>", self.on_region_motion)

        self.min_range = 50
        self.max_range = 450

        self.draw_grid()

        self.save_button = tk.Button(self.window, text="Save", command=self.save_points)
        self.save_button.pack(side=tk.LEFT)

        self.load_button = tk.Button(self.window, text="Load", command=self.load_points)
        self.load_button.pack(side=tk.LEFT)

    def on_button_press(self, event):
        self.selected_point = event.widget.find_withtag("current")[0]
    
    def on_motion(self, event):
        if self.selected_point is not None:
            index = int(self.canvas.gettags(self.selected_point)[0][5:])
            x = 20 * index
            y = max(self.min_range, min(event.y, self.max_range))
            self.canvas.coords(self.selected_point, x-5, y-5, x+5, y+5)
            self.update_lines()
            self.apply_tone_curve()

    def on_region_press(self, event):
        region_index = int(self.canvas.gettags("current")[0][6:])
        self.selected_point = self.points[region_index]

    def on_region_motion(self, event):
        self.on_motion(event)

    def update_lines(self):
        for line in self.lines:
            self.canvas.delete(line)
        self.lines = []
        for i in range(len(self.points) - 1):
            x1, y1, _, _ = self.canvas.coords(self.points[i])
            x2, y2, _, _ = self.canvas.coords(self.points[i + 1])
            line = self.canvas.create_line(x1+5, y1+5, x2+5, y2+5, fill="white")
            self.lines.append(line)

    def draw_grid(self):
        for i in range(0, 501, 50):
            self.canvas.create_line(i, 0, i, 500, fill="#696969")
            self.canvas.create_line(0, i, 500, i, fill="#696969")
        
        for i in range(0, 501, 50):
            self.canvas.create_text(i, 490, text=str(i), fill="white")
            self.canvas.create_text(10, 500-i, text=str(i), fill="white")

    def apply_tone_curve(self):
        curve = np.zeros(256)
        for i in range(len(self.points)):
            x, y, _, _ = self.canvas.coords(self.points[i])
            curve[int(255 * (x / 500))] = 255 * (1 - y / 500)
        curve = np.interp(np.arange(256), np.where(curve != 0)[0], curve[curve != 0])
        
        lut = np.array([curve[int(i)] for i in range(256)]).astype("uint8")
        updated_image = ImageOps.autocontrast(self.image.point(lut))
        self.main_app.update_image(updated_image)

    def save_points(self):
        points_data = {}
        for i, point in enumerate(self.points):
            _, y1, _, y2 = self.canvas.coords(point)
            points_data[f"point{i}"] = {"x": 20 * i, "y": (y1 + y2) / 2}

        df = pd.DataFrame(points_data).T
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            df.to_excel(save_path, index=False)

    def load_points(self):
        load_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if load_path:
            df = pd.read_excel(load_path)
            for i, point in df.iterrows():
                x = point["x"]
                y = point["y"]
                self.canvas.coords(self.points[i], x-5, y-5, x+5, y+5)
            self.update_lines()
            self.apply_tone_curve()

root = tk.Tk()
app = ToneCurveApp(root, "niwatori.jpg")
root.mainloop()
