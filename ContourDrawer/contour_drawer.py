import tkinter as tk
from tkinter import Canvas, filedialog, ttk
from PIL import Image, ImageTk
import uuid

class ContourDrawer:
    def __init__(self, canvas, color_var, img_size):
        self.canvas = canvas
        self.color_var = color_var
        self.img_size = img_size

        self.drawing = False
        self.current_points = []
        self.current_line = None
        self.contours = {}  # Store contours with unique IDs

        self.set_bindings()

    def set_bindings(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_contour)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drawing)
        #self.canvas.bind("<Double-Button-1>", self.finish_drawing)  # Double-click to finish drawing
        self.canvas.focus_set()

    def start_drawing(self, event):
        if not self.drawing:
            self.drawing = True
            self.current_points = [(event.x, event.y)]
            self.current_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill=self.color_var.get(), width=2)

    def draw_contour(self, event):
        if self.drawing:
            self.current_points.append((event.x, event.y))
            self.canvas.coords(self.current_line, *self.flatten_points(self.current_points))

    def finish_drawing(self, event):
        if self.drawing:
            # Close the polygon by connecting to the start point
            self.current_points.append(self.current_points[0])

            # Create unique tag for this contour
            contour_id = str(uuid.uuid4())
            polygon = self.canvas.create_polygon(
                self.flatten_points(self.current_points),
                fill=self.color_var.get(),
                outline=self.color_var.get(),
                stipple='gray50',
                tags=contour_id
            )

            # Remove the temporary line
            self.canvas.delete(self.current_line)

            # Store the contour data
            self.contours[contour_id] = {
                'points': self.get_original_points(self.current_points),
                'polygon_id': polygon,
                'color': self.color_var.get()
            }

            # Reset drawing state
            self.drawing = False
            self.current_points = []
            self.current_line = None

    def flatten_points(self, points):
        return [coord for point in points for coord in point]

    def get_original_points(self, points):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.img_size

        x_ratio = img_width / canvas_width
        y_ratio = img_height / canvas_height

        original_points = [(int(x * x_ratio), int(y * y_ratio)) for x, y in points]
        return original_points

    def get_contour(self, contour_id):
        return self.contours.get(contour_id, None)

    def delete_contour(self, contour_id):
        if contour_id in self.contours:
            self.canvas.delete(self.contours[contour_id]['polygon_id'])
            del self.contours[contour_id]

class Deleter:
    def __init__(self, canvas, drawer):
        self.canvas = canvas
        self.drawer = drawer
        self.selected_contour_id = None

        self.set_bindings()

    def set_bindings(self):
        self.canvas.bind("<ButtonPress-3>", self.select_contour)
        self.canvas.bind("<KeyPress-Delete>", self.delete_contour)
        self.canvas.bind("<KeyPress-Escape>", self.deselect_contour)
        self.canvas.focus_set()

    def select_contour(self, event):
        # Deselect previous selection
        if self.selected_contour_id:
            self.canvas.itemconfig(self.selected_contour_id, outline=self.drawer.contours[self.selected_contour_id]['color'], width=1)
            self.selected_contour_id = None

        # Find items under cursor
        items = self.canvas.find_withtag("current")
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag in self.drawer.contours:
                    self.selected_contour_id = tag
                    self.canvas.itemconfig(item, outline='red', width=2)
                    return

    def delete_contour(self, event=None):
        if self.selected_contour_id:
            self.drawer.delete_contour(self.selected_contour_id)
            self.selected_contour_id = None

    def deselect_contour(self, event=None):
        if self.selected_contour_id:
            self.canvas.itemconfig(self.selected_contour_id, outline=self.drawer.contours[self.selected_contour_id]['color'], width=1)
            self.selected_contour_id = None

class ContourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contour Drawer")

        # Frame for controls
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Load Image Button
        self.load_button = tk.Button(control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Color selection Combobox
        self.color_var = tk.StringVar(value='blue')
        self.color_combobox = ttk.Combobox(control_frame, textvariable=self.color_var, values=['blue', 'green', 'red', 'yellow', 'purple', 'orange'], state="readonly", width=10)
        self.color_combobox.pack(side=tk.LEFT, padx=5)

        # Canvas setup
        self.canvas = Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize Drawer and Deleter
        self.drawer = None
        self.deleter = None

        # Original image size
        self.img_size = (800, 600)
        self.img = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            original_img = Image.open(file_path)
            self.img_size = original_img.size
            img = self.resize_image_to_canvas(original_img)
            self.img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")  # Clear previous content
            self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

            # Initialize Drawer and Deleter
            self.drawer = ContourDrawer(self.canvas, self.color_var, self.img_size)
            self.deleter = Deleter(self.canvas, self.drawer)

    def resize_image_to_canvas(self, img):
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(new_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(new_height * img_ratio)

        return img.resize((new_width, new_height), Image.LANCZOS)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContourApp(root)
    root.mainloop()
