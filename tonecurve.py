import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import numpy as np

class ToneCurveApp:
    def __init__(self, root, image_path, min_range=50, max_range=450):
        self.root = root
        self.root.title("Tone Curve Adjustment")
        
        self.canvas = tk.Canvas(root, width=500, height=500)
        self.canvas.pack()
        
        self.image = Image.open(image_path).convert("L")
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        self.points = [self.canvas.create_oval(20 * i, 480, 20 * i + 5, 485, fill="blue") for i in range(25)]
        self.lines = []
        self.update_lines()
        
        for point in self.points:
            self.canvas.tag_bind(point, "<ButtonPress-1>", self.on_button_press)
            self.canvas.tag_bind(point, "<B1-Motion>", self.on_motion)
        
        self.selected_point = None
        self.min_range = min_range
        self.max_range = max_range
    
    def on_button_press(self, event):
        self.selected_point = event.widget.find_withtag("current")[0]
    
    def on_motion(self, event):
        _, _, x2, _ = self.canvas.coords(self.selected_point)
        y = max(self.min_range, min(event.y, self.max_range))
        self.canvas.coords(self.selected_point, x2-5, y, x2, y+5)
        self.update_lines()
        self.apply_tone_curve()
    
    def update_lines(self):
        for line in self.lines:
            self.canvas.delete(line)
        self.lines = []
        for i in range(len(self.points) - 1):
            x1, y1, _, _ = self.canvas.coords(self.points[i])
            x2, y2, _, _ = self.canvas.coords(self.points[i + 1])
            line = self.canvas.create_line(x1, y1, x2, y2, fill="blue")
            self.lines.append(line)
    
    def apply_tone_curve(self):
        curve = np.zeros(256)
        for i in range(len(self.points)):
            x, y, _, _ = self.canvas.coords(self.points[i])
            curve[int(255 * (x / 500))] = 255 * (1 - y / 500)
        curve = np.interp(np.arange(256), np.where(curve != 0)[0], curve[curve != 0])
        
        lut = np.array([curve[int(i)] for i in range(256)]).astype("uint8")
        self.updated_image = ImageOps.autocontrast(self.image.point(lut))
        self.photo = ImageTk.PhotoImage(self.updated_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

root = tk.Tk()
app = ToneCurveApp(root, "path_to_your_image.jpg")
root.mainloop()
