import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np

class ImageProcessor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Processor")
        self.configure_window()

        self.image_handler = ImageHandler()
        self.shape_drawer = ShapeDrawer()
        
        self.canvas_handler = CanvasHandler(self, self.image_handler, self.shape_drawer)
        self.canvas_handler.pack(fill=tk.BOTH, expand=True)

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)

    def configure_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = screen_width * 3 // 4
        window_height = screen_height * 3 // 4
        self.geometry(f"{window_width}x{window_height}+{screen_width//8}+{screen_height//8}")

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_handler.load_image(file_path)
            self.canvas_handler.reset_view()

class ImageHandler:
    def __init__(self):
        self.image = None
        self.image_scale = 1.0
        self.shapes = []

    def load_image(self, file_path):
        self.image = cv2.imread(file_path)
        self.process_image()

    def process_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
        circles = [] if circles is None else circles[0, :].astype("int")

        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=10)
        rectangles = [] if lines is None else [cv2.boundingRect(line.reshape(-1, 2)) for line in lines]

        self.shapes = [(*circle, "circle") for circle in circles] + [(*rect, "rectangle") for rect in rectangles]

class ShapeDrawer:
    def __init__(self):
        self.tk_image = None

    def update_image(self, canvas, image, shapes, zoom_level, offset_x, offset_y, highlight_shape=None):
        if image is None:
            return
        
        h, w = image.shape[:2]
        window_w, window_h = canvas.winfo_width(), canvas.winfo_height()

        if w / window_w > h / window_h:
            image_scale = window_w / w
        else:
            image_scale = window_h / h

        scaled_size = (int(w * image_scale * zoom_level), int(h * image_scale * zoom_level))
        scaled_image = cv2.resize(image, scaled_size)
        
        pil_image = Image.fromarray(cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        for shape in shapes:
            if shape[-1] == "circle":
                x, y, r = shape[:3]
                x, y, r = int(x * image_scale * zoom_level), int(y * image_scale * zoom_level), int(r * image_scale * zoom_level)
                color = "red" if shape == highlight_shape else "green"
                draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=2 if shape == highlight_shape else 1)
            elif shape[-1] == "rectangle":
                x, y, w, h = shape[:4]
                x, y, w, h = int(x * image_scale * zoom_level), int(y * image_scale * zoom_level), int(w * image_scale * zoom_level), int(h * image_scale * zoom_level)
                color = "red" if shape == highlight_shape else "blue"
                draw.rectangle((x, y, x + w, y + h), outline=color, width=2 if shape == highlight_shape else 1)

        self.tk_image = ImageTk.PhotoImage(pil_image)
        canvas.delete("all")
        canvas.create_image(window_w//2 + offset_x, window_h//2 + offset_y, anchor=tk.CENTER, image=self.tk_image)

    def find_highlight_shape(self, x, y, shapes, image_scale, zoom_level):
        for shape in shapes:
            if shape[-1] == "circle":
                cx, cy, r = shape[:3]
                scaled_cx, scaled_cy, scaled_r = cx * image_scale * zoom_level, cy * image_scale * zoom_level, r * image_scale * zoom_level
                if (scaled_cx - x) ** 2 + (scaled_cy - y) ** 2 <= scaled_r ** 2:
                    return shape
            elif shape[-1] == "rectangle":
                rx, ry, rw, rh = shape[:4]
                scaled_rx, scaled_ry, scaled_rw, scaled_rh = rx * image_scale * zoom_level, ry * image_scale * zoom_level, rw * image_scale * zoom_level, rh * image_scale * zoom_level
                if scaled_rx <= x <= scaled_rx + scaled_rw and scaled_ry <= y <= scaled_ry + scaled_rh:
                    return shape
        return None

class CanvasHandler(tk.Canvas):
    def __init__(self, master, image_handler, shape_drawer):
        super().__init__(master, bg="white", highlightthickness=0)
        self.master = master
        self.image_handler = image_handler
        self.shape_drawer = shape_drawer

        self.zoom_level = 1.0
        self.pan_start = None
        self.offset_x = 0
        self.offset_y = 0

        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<ButtonPress-2>", self.on_pan_start)
        self.bind("<B2-Motion>", self.on_pan_move)

    def reset_view(self):
        self.zoom_level = 1.0
        self.offset_x = self.offset_y = 0
        self.update_image()

    def on_mouse_move(self, event):
        if self.image_handler.image is None:
            return

        # マウス座標をキャンバス座標に変換
        canvas_x = event.x - self.offset_x - self.winfo_width() // 2
        canvas_y = event.y - self.offset_y - self.winfo_height() // 2

        # キャンバス座標を画像座標に変換
        image_x = canvas_x / (self.image_handler.image_scale * self.zoom_level)
        image_y = canvas_y / (self.image_handler.image_scale * self.zoom_level)

        # ハイライトする図形を見つける
        highlight_shape = self.shape_drawer.find_highlight_shape(image_x, image_y, self.image_handler.shapes, self.image_handler.image_scale, self.zoom_level)
        self.update_image(highlight_shape)

    def on_mouse_wheel(self, event):
        if self.image_handler.image is None:
            return
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_level *= scale_factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))
        self.update_image()

    def on_pan_start(self, event):
        self.pan_start = (event.x, event.y)

    def on_pan_move(self, event):
        if self.pan_start is None:
            return
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]
        self.offset_x += dx
        self.offset_y += dy
        self.pan_start = (event.x, event.y)
        self.update_image()

    def update_image(self, highlight_shape=None):
        self.shape_drawer.update_image(self, self.image_handler.image, self.image_handler.shapes, self.zoom_level, self.offset_x, self.offset_y, highlight_shape)

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()
