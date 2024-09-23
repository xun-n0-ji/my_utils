import tkinter as tk
from tkinter import Canvas, filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import uuid

class ContourDrawer:
    def __init__(self, canvas, color_var, img_size, label_dir, cutout_canvas=None, app=None):
        self.canvas = canvas
        self.color_var = color_var
        self.img_size = img_size
        self.cutout_canvas = cutout_canvas
        self.label_dir = label_dir
        self.app = app  # ContourApp インスタンスを保持

        self.drawing = False
        self.current_points = []
        self.current_line = None
        self.contours = {}
        self.selected_contour_id = None

        self.set_bindings()

    def set_bindings(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_contour)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drawing)
        self.canvas.focus_set()

        # Bind mouse events for color change
        self.cutout_canvas.bind("<Motion>", self.on_mouse_move)
        self.cutout_canvas.bind("<ButtonPress-1>", self.on_left_click)
        self.cutout_canvas.bind("<KeyPress-s>", self.delete_selected_contour)

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
            self.current_points.append(self.current_points[0])
            contour_id = str(uuid.uuid4())
            polygon = self.canvas.create_polygon(
                self.flatten_points(self.current_points),
                fill='',  # No fill for now
                outline=self.color_var.get(),
                width=2,
                tags=contour_id
            )
            self.canvas.delete(self.current_line)

            self.contours[contour_id] = {
                'points': self.get_original_points(self.current_points),
                'polygon_id': polygon,
                'color': self.color_var.get(),
                'selected': False  # Keep track of selection state
            }

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

        self.x_ratio = x_ratio
        self.y_ratio = y_ratio

        original_points = [(int(x * x_ratio), int(y * y_ratio)) for x, y in points]
        return original_points

    def draw_contours_on_image(self, img_cv, contours):
        overlay = img_cv.copy()  # Create a copy for overlay
        for contour_data in contours.values():
            points = np.array(contour_data['points'], dtype=np.int32)

            # Fill the contour with a semi-transparent color (blue in this case)
            cv2.fillPoly(overlay, [points], color=(255, 0, 0))  # Blue fill

            # Draw the contour line (full opacity)
            cv2.polylines(overlay, [points], isClosed=True, color=(0, 0, 255), thickness=2)  # Red outline

        # Combine the original image with the overlay using transparency
        img_with_overlay = cv2.addWeighted(img_cv, 0.7, overlay, 0.3, 0)  # 30% transparency

        return img_with_overlay

    def cutout_contour(self, contour_id, image_filepath):
        if contour_id in self.contours:
            contour_data = self.contours[contour_id]

            # Load the original image in OpenCV
            img_cv = cv2.imread(image_filepath)
            mask = np.zeros_like(img_cv, dtype=np.uint8)  # Create a blank mask the same size as the original image

            # Extract the contour points
            points = np.array(contour_data['points'], dtype=np.int32)

            # Draw the filled contour on the mask with white color
            cv2.fillPoly(mask, [points], (255, 255, 255))

            # Create the overlay with the desired color (blue in this case)
            overlay = img_cv.copy()
            cv2.fillPoly(overlay, [points], color=(255, 0, 0))  # Blue fill for the contour

            # Combine the original image and overlay with transparency (30% overlay, 70% original)
            img_with_overlay = cv2.addWeighted(img_cv, 0.7, overlay, 0.3, 0)

            # Apply the mask to retain only the contour area with transparency
            mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            img_with_overlay = np.where(mask_gray[:, :, None] == 255, img_with_overlay, img_cv)

            # Convert the resulting image to PIL for display
            img_pil = Image.fromarray(cv2.cvtColor(img_with_overlay, cv2.COLOR_BGR2RGB))
            img_resized = self.app.resize_image_to_canvas(img_pil)
            self.img_cutout = ImageTk.PhotoImage(img_resized)

            # Display the cutout image
            self.cutout_canvas.delete("all")
            self.cutout_canvas.create_image(0, 0, anchor="nw", image=self.img_cutout)

            # Save the label and remove contour
            self.save_label(os.path.splitext(os.path.basename(image_filepath))[0], contour_data)

    def save_label(self, image_filename, contour_data):
        os.makedirs(self.label_dir, exist_ok=True)
        label_filename = os.path.join(self.label_dir, f"{image_filename}.txt")
        with open(label_filename, "a") as file:
            class_id = 0  # For now, using class_id=0, can modify this logic
            points = contour_data['points']
            points_str = " ".join([f"{x} {y}" for x, y in points])
            file.write(f"{class_id} {points_str}\n")

    def load_labels(self, image_filename, img_cv):
        label_filename = os.path.join(self.label_dir, f"{image_filename}.txt")
        if os.path.exists(label_filename):
            with open(label_filename, "r") as file:
                overlay = img_cv.copy()  # オーバーレイ用に画像をコピー
                for line in file.readlines():
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    points = np.array([[int(parts[i]), int(parts[i+1])] for i in range(1, len(parts), 2)], dtype=np.int32)

                    # オーバーレイに輪郭を半透明で塗りつぶす（青色）
                    cv2.fillPoly(overlay, [points], (255, 0, 0))  # 青色で塗りつぶす

                # 元の画像とオーバーレイを半透明で合成（30% オーバーレイ、70% 元の画像）
                img_with_overlay = cv2.addWeighted(img_cv, 0.7, overlay, 0.3, 0)

        else:
            img_with_overlay = img_cv  # ラベルがない場合は元の画像のまま

        return img_with_overlay

    def on_mouse_move(self, event):
        for contour_id, contour_data in self.contours.items():
            if self.is_point_inside_contour(event.x, event.y, contour_data['points']):
                if not contour_data['selected']:
                    self.highlight_contour(contour_id, "deep")
            else:
                if not contour_data['selected']:
                    self.highlight_contour(contour_id, "light")

    def is_point_inside_contour(self, x, y, points):
        return cv2.pointPolygonTest(np.array(points), (x*self.x_ratio, y*self.y_ratio), False) >= 0

    def highlight_contour(self, contour_id, intensity):
        contour_data = self.contours[contour_id]
        color = contour_data['color']

        # 色の調整
        if intensity == "deep":
            alpha = 0.7  # 深い色の時の透明度（濃い色）
        else:
            alpha = 0.3  # 明るい色の時の透明度（薄い色）

        # OpenCVで扱うために色をBGRフォーマットに変換
        bgr_color = self.name_to_bgr(color)

        # 元の画像を取得
        img_cv = cv2.imread(self.app.file_path)

        # オーバーレイ作成
        overlay = img_cv.copy()
        points = np.array(contour_data['points'], dtype=np.int32)

        # オーバーレイに輪郭を塗りつぶし
        cv2.fillPoly(overlay, [points], bgr_color)

        # オーバーレイと元の画像を合成
        img_with_overlay = cv2.addWeighted(img_cv, 1 - alpha, overlay, alpha, 0)

        # 結果をPILに変換して表示
        img_pil = Image.fromarray(cv2.cvtColor(img_with_overlay, cv2.COLOR_BGR2RGB))
        img_resized = self.app.resize_image_to_canvas(img_pil)
        self.img_cutout = ImageTk.PhotoImage(img_resized)

        # 表示を更新
        self.cutout_canvas.delete("all")
        self.cutout_canvas.create_image(0, 0, anchor="nw", image=self.img_cutout)

    def name_to_bgr(self, color_name):
        """色名からOpenCV用のBGRフォーマットに変換"""
        color_map = {
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'yellow': (0, 255, 255),
            'purple': (128, 0, 128),
            'orange': (0, 165, 255)
        }
        return color_map.get(color_name, (255, 255, 255))  # デフォルトは白色

    def adjust_color_brightness(self, color_name, factor):
        color_map = {
            'blue': '#0000FF',
            'green': '#008000',
            'red': '#FF0000',
            'yellow': '#FFFF00',
            'purple': '#800080',
            'orange': '#FFA500'
        }
        hex_color = color_map[color_name]
        rgb_color = self.hex_to_rgb(hex_color)
        adjusted_rgb = tuple(min(int(c * factor), 255) for c in rgb_color)
        return self.rgb_to_hex(adjusted_rgb)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        return "#{:02x}{:02x}{:02x}".format(*rgb_color)

    def on_left_click(self, event):
        for contour_id, contour_data in self.contours.items():
            if self.is_point_inside_contour(event.x, event.y, contour_data['points']):
                self.select_contour(contour_id)

    def select_contour(self, contour_id):
        # Unselect previous contour if any
        if self.selected_contour_id is not None and self.selected_contour_id in self.contours:
            self.unselect_contour(self.selected_contour_id)

        # Select new contour
        self.selected_contour_id = contour_id
        self.contours[contour_id]['selected'] = True
        self.cutout_canvas.itemconfig(self.contours[contour_id]['polygon_id'], outline='red')

    def unselect_contour(self, contour_id):
        self.contours[contour_id]['selected'] = False
        self.cutout_canvas.itemconfig(self.contours[contour_id]['polygon_id'], outline=self.contours[contour_id]['color'])

    def delete_selected_contour(self, event):
        if self.selected_contour_id is not None and self.selected_contour_id in self.contours:
            contour_data = self.contours[self.selected_contour_id]
            self.cutout_canvas.delete(contour_data['polygon_id'])
            del self.contours[self.selected_contour_id]
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

        # Cutout Button
        self.cutout_button = tk.Button(control_frame, text="Cutout", command=self.cutout_contour)
        self.cutout_button.pack(side=tk.LEFT, padx=5)

        # Color selection Combobox
        self.color_var = tk.StringVar(value='blue')
        self.color_combobox = ttk.Combobox(control_frame, textvariable=self.color_var, values=['blue', 'green', 'red', 'yellow', 'purple', 'orange'], state="readonly", width=10)
        self.color_combobox.pack(side=tk.LEFT, padx=5)

        # Canvas setup for edit and cutout
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = Canvas(canvas_frame, width=400, height=600, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cutout_canvas = Canvas(canvas_frame, width=400, height=600, bg='white')
        self.cutout_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize Drawer
        self.drawer = None
        self.img_size = (800, 600)
        self.img = None
        self.image_filename = ""
        self.label_dir = "labels"

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            original_img = Image.open(file_path)
            self.img_size = original_img.size
            self.file_path = file_path
            self.image_filename = os.path.splitext(os.path.basename(file_path))[0]
            img = self.resize_image_to_canvas(original_img)
            self.img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.cutout_canvas.delete("all")

            # Display the image on both canvases
            self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            self.cutout_canvas.create_image(0, 0, anchor="nw", image=self.img)

            # Initialize Drawer
            self.drawer = ContourDrawer(self.canvas, self.color_var, self.img_size, self.label_dir, self.cutout_canvas, app=self)

            # Check for existing labels and display them on cutout_canvas
            self.load_labels_from_file()

    def resize_image_to_canvas(self, img):
        canvas_width = self.canvas.winfo_width() or 400
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

    def cutout_contour(self):
        selected_id = next(iter(self.drawer.contours.keys()), None)
        if selected_id:
            self.drawer.cutout_contour(selected_id, self.file_path)
            self.load_labels_from_file()  # Update the cutout_canvas with labels after cutout

    def load_labels_from_file(self):
        img_cv = cv2.imread(self.file_path)  # Load original image
        img_cv = self.drawer.load_labels(self.image_filename, img_cv)

        # Draw all the contours on the image
        img_cv_with_contours = self.drawer.draw_contours_on_image(img_cv, self.drawer.contours)

        # Convert OpenCV image to PIL for display on cutout_canvas
        img_pil = Image.fromarray(cv2.cvtColor(img_cv_with_contours, cv2.COLOR_BGR2RGB))
        img_resized = self.resize_image_to_canvas(img_pil)
        self.img_cutout = ImageTk.PhotoImage(img_resized)

        self.cutout_canvas.delete("all")
        self.cutout_canvas.create_image(0, 0, anchor="nw", image=self.img_cutout)


if __name__ == "__main__":
    root = tk.Tk()
    app = ContourApp(root)
    root.mainloop()
