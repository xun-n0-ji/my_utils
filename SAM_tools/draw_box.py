import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageDraw
import os

class RectDrawer:
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.color = color
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rects = []

    def activate(self):
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def deactivate(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline=self.color, tag="rectangle")

    def on_button_release(self, event):
        if self.rect:
            self.rects.append((self.start_x, self.start_y, event.x, event.y, self.color))
            self.rect = None

    def get_rects(self):
        return self.rects

    def set_rects(self, rects):
        self.clear_rects()
        for rect in rects:
            x1, y1, x2, y2, color = rect
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, tag="rectangle")
        self.rects = rects

    def clear_rects(self):
        self.rects = []
        self.canvas.delete("rectangle")

class PointDrawer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.points = []

    def activate(self):
        self.canvas.bind("<Button-1>", self.mark_circle_in_green)
        self.canvas.bind("<Button-3>", self.mark_cross_in_red)

    def deactivate(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")

    def mark_circle_in_green(self, event):
        x, y = event.x, event.y
        point = self.canvas.create_oval(x-5, y-5, x+5, y+5, outline="green", width=2, tag="circle")
        self.points.append(('circle', point))

    def mark_cross_in_red(self, event):
        x, y = event.x, event.y
        point = self.canvas.create_line(x-5, y-5, x+5, y+5, fill="red", width=2, tag="cross")
        point2 = self.canvas.create_line(x+5, y-5, x-5, y+5, fill="red", width=2, tag="cross")
        self.points.append(('cross', point, point2))

    def get_points(self):
        return self.points

    def set_points(self, points):
        self.clear_points()
        for point in points:
            if point[0] == 'circle':
                x1, y1, x2, y2 = self.canvas.coords(point[1])
                self.canvas.create_oval(x1, y1, x2, y2, outline="green", width=2, tag="circle")
            elif point[0] == 'cross':
                x1, y1, x2, y2 = self.canvas.coords(point[1])
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, tag="cross")
                x1, y1, x2, y2 = self.canvas.coords(point[2])
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2, tag="cross")
        self.points = points

    def clear_points(self):
        self.points = []
        self.canvas.delete("circle")
        self.canvas.delete("cross")

class LabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling App")

        self.label_colors = {
            "Label 1": "red",
            "Label 2": "blue",
            "Label 3": "green",
        }

        self.image_paths = []
        self.image_index = 0
        self.image = None
        self.rects = {}
        self.points = {}
        self.current_label = tk.StringVar()
        self.current_label.set("Label 1")
        self.current_mode = tk.StringVar(value="box")

        self.undo_stack = []
        self.redo_stack = []

        self.create_widgets()
        self.bind_shortcuts()

    def create_widgets(self):
        # Left frame for controls and main canvas
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Open File button
        open_button = tk.Button(left_frame, text="Open File", command=self.open_file)
        open_button.pack(pady=10)

        # Main Canvas
        self.main_canvas = tk.Canvas(left_frame, bg="white")
        self.main_canvas.pack(fill=tk.BOTH, expand=True)

        self.rect_drawer = RectDrawer(self.main_canvas, self.label_colors[self.current_label.get()])
        self.point_drawer = PointDrawer(self.main_canvas)
        self.switch_drawer()

        # Label Combobox
        label_combobox = ttk.Combobox(left_frame, textvariable=self.current_label)
        label_combobox['values'] = list(self.label_colors.keys())
        label_combobox.pack(pady=10)
        label_combobox.bind("<<ComboboxSelected>>", self.update_color)

        # Mode Radiobuttons
        modes_frame = tk.Frame(left_frame)
        modes_frame.pack(pady=10)
        tk.Radiobutton(modes_frame, text="Box", variable=self.current_mode, value="box", command=self.switch_drawer).pack(side=tk.LEFT)
        tk.Radiobutton(modes_frame, text="Point", variable=self.current_mode, value="point", command=self.switch_drawer).pack(side=tk.LEFT)

        # Apply Button
        apply_button = tk.Button(left_frame, text="Apply", command=self.apply_labels)
        apply_button.pack(pady=10)

        # Next and Previous Buttons
        prev_button = tk.Button(left_frame, text="Prev", command=self.prev_image)
        prev_button.pack(side=tk.LEFT, padx=10)
        next_button = tk.Button(left_frame, text="Next", command=self.next_image)
        next_button.pack(side=tk.RIGHT, padx=10)

        # Right frame for labeled image canvas and combobox
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Labeled Image Canvas
        self.labeled_canvas = tk.Canvas(right_frame, bg="white", width=300, height=300)
        self.labeled_canvas.pack(pady=10)

        # Labeled Combobox
        self.labeled_combobox = ttk.Combobox(right_frame, values=list(self.label_colors.keys()))
        self.labeled_combobox.pack(pady=10)
        self.labeled_combobox.bind("<<ComboboxSelected>>", self.update_labeled_canvas)

    def switch_drawer(self):
        self.rect_drawer.deactivate()
        self.point_drawer.deactivate()
        if self.current_mode.get() == "box":
            self.rect_drawer.activate()
        elif self.current_mode.get() == "point":
            self.point_drawer.activate()

    def bind_shortcuts(self):
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

    def open_file(self):
        image_filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        image_dir = os.path.dirname(image_filepath)
        if image_dir:
            self.image_paths = [os.path.join(image_dir, f).replace("\\", "/") for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            if self.image_paths:
                self.image_index = self.image_paths.index(image_filepath)
                self.load_image()

    def load_image(self):
        self.image = Image.open(self.image_paths[self.image_index])
        self.display_image(self.image, self.main_canvas, "main")
        if self.image_paths[self.image_index] in self.rects:
            self.rect_drawer.set_rects(self.rects[self.image_paths[self.image_index]])
        else:
            self.rect_drawer.clear_rects()

        if self.image_paths[self.image_index] in self.points:
            self.point_drawer.set_points(self.points[self.image_paths[self.image_index]])
        else:
            self.point_drawer.clear_points()

    def display_image(self, image, canvas, tag):
        tk_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image, tag=tag)
        canvas.image = tk_image
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

    def update_color(self, event):
        color = self.label_colors[self.current_label.get()]
        self.rect_drawer.color = color

    def apply_labels(self):
        if self.image:
            labeled_image = self.image.copy()
            draw = ImageDraw.Draw(labeled_image)
            rects = self.rect_drawer.get_rects()
            points = self.point_drawer.get_points()

            for rect in rects:
                x1, y1, x2, y2, color = rect
                draw.rectangle([x1, y1, x2, y2], outline=color)

            for point in points:
                if point[0] == 'circle':
                    x1, y1, x2, y2 = self.main_canvas.coords(point[1])
                    draw.ellipse([x1, y1, x2, y2], outline="green", width=2)
                elif point[0] == 'cross':
                    x1, y1, x2, y2 = self.main_canvas.coords(point[1])
                    draw.line([x1, y1, x2, y2], fill="red", width=2)
                    x1, y1, x2, y2 = self.main_canvas.coords(point[2])
                    draw.line([x1, y1, x2, y2], fill="red", width=2)

            self.display_image(labeled_image, self.labeled_canvas, "labeled")
            self.rects[self.image_paths[self.image_index]] = rects
            self.points[self.image_paths[self.image_index]] = points

    def update_combobox(self):
        labels = list(set([self.current_label.get() for rect in self.rects]))
        self.labeled_combobox['values'] = labels

    def update_labeled_canvas(self, event):
        selected_label = self.labeled_combobox.get()
        if self.image and selected_label:
            labeled_image = self.image.copy()
            draw = ImageDraw.Draw(labeled_image)
            for rect in self.rects.get(self.image_paths[self.image_index], []):
                if rect[4] == self.label_colors[selected_label]:
                    x1, y1, x2, y2, color = rect
                    draw.rectangle([x1, y1, x2, y2], outline=color)
            self.display_image(labeled_image, self.labeled_canvas, "labeled")

    def next_image(self):
        if self.image_paths and self.image_index < len(self.image_paths) - 1:
            self.image_index += 1
            self.load_image()
            self.apply_labels()

    def prev_image(self):
        if self.image_paths and self.image_index > 0:
            self.image_index -= 1
            self.load_image()
            self.apply_labels()

    def undo(self, event=None):
        if self.rect_drawer.get_rects():
            self.redo_stack.append(('rect', self.rect_drawer.get_rects().pop()))
            self.rect_drawer.set_rects(self.rect_drawer.get_rects())
            self.apply_labels()
        elif self.point_drawer.get_points():
            self.redo_stack.append(('point', self.point_drawer.get_points().pop()))
            self.point_drawer.set_points(self.point_drawer.get_points())
            self.apply_labels()

    def redo(self, event=None):
        if self.redo_stack:
            action, item = self.redo_stack.pop()
            if action == 'rect':
                self.rect_drawer.get_rects().append(item)
                self.rect_drawer.set_rects(self.rect_drawer.get_rects())
            elif action == 'point':
                self.point_drawer.get_points().append(item)
                self.point_drawer.set_points(self.point_drawer.get_points())
            self.apply_labels()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
