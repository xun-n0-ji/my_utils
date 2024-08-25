import tkinter as tk
from tkinter import Canvas, filedialog, ttk
from PIL import Image, ImageTk

class ContourDrawer:
    def __init__(self, canvas, color_var, img_size):
        self.canvas = canvas
        self.start_x = None
        self.start_y = None
        self.points = []
        self.line_id = None
        self.color_var = color_var
        self.current_polygon = None
        self.img_size = img_size
        self.contour_id = 0  # 輪郭ごとの一意なID
        self.set_binding()

    def set_binding(self):
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_contour)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drawing)
        self.canvas.focus_set()

    def start_drawing(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.points = [(self.start_x, self.start_y)]
        self.current_polygon = None

    def draw_contour(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.points.append((event.x, event.y))
            if self.line_id is None:
                self.line_id = self.canvas.create_line(
                    self.start_x, self.start_y, event.x, event.y,
                    fill=self.color_var.get(), width=2
                )
            else:
                flattened_points = [coord for point in self.points for coord in point]
                self.canvas.coords(self.line_id, *flattened_points)

    def finish_drawing(self, event):
        if self.line_id is not None:
            self.points.append((self.start_x, self.start_y))
            flattened_points = [coord for point in self.points for coord in point]
            self.canvas.coords(self.line_id, *flattened_points)
            self.current_polygon = self.canvas.create_polygon(
                flattened_points,
                fill=self.color_var.get(),
                stipple='gray25',
                outline=self.color_var.get()
            )
            
            # 一意なタグを生成し、線とポリゴンに付与
            self.contour_id += 1
            tag = f"contour_{self.contour_id}"
            self.canvas.itemconfig(self.line_id, tags=(tag,))
            self.canvas.itemconfig(self.current_polygon, tags=(tag,))
            
            # リセット
            self.line_id = None
            self.points = []

    def get_contour(self):
        """
        現在の輪郭の座標を、リサイズ前のオリジナル画像に対応する座標に変換して返します。
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.img_size

        x_ratio = img_width / canvas_width
        y_ratio = img_height / canvas_height

        original_points = [(int(x * x_ratio), int(y * y_ratio)) for x, y in self.points]
        return original_points

class Deleter:
    def __init__(self, canvas):
        self.canvas = canvas
        self.selected_tag = None
        self.set_bind()

    def set_bind(self):
        # 右クリックで選択、DeleteキーやEscapeキーで削除
        self.canvas.bind("<ButtonPress-3>", self.select_polygon)
        self.canvas.bind("<KeyPress-Delete>", self.delete_polygon)
        self.canvas.bind("<KeyPress-Escape>", self.delete_polygon)
        self.canvas.focus_set()

    def select_polygon(self, event):
        # すべてのポリゴンのアウトラインを元に戻す
        polygons = [item for item in self.canvas.find_all() if self.canvas.type(item) == 'polygon']
        for poly in polygons:
            fill_color = self.canvas.itemcget(poly, 'fill')
            self.canvas.itemconfig(poly, outline=fill_color)
        
        # クリックした位置にあるポリゴンを選択
        overlapping_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in overlapping_items:
            if self.canvas.type(item) == 'polygon':
                tags = self.canvas.gettags(item)
                if tags:
                    self.selected_tag = tags[0]
                    # 選択したポリゴンのアウトラインを赤に変更
                    self.canvas.itemconfig(item, outline='red')
                    break

    def delete_polygon(self, event=None):
        if self.selected_tag is not None:
            # 選択されたタグを持つすべてのアイテム（線とポリゴン）を削除
            for item in self.canvas.find_withtag(self.selected_tag):
                self.canvas.delete(item)
            self.selected_tag = None

class ContourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contour Drawer")

        # 色選択のコンボボックス
        self.color_var = tk.StringVar(value='blue')
        self.color_combobox = ttk.Combobox(
            root,
            textvariable=self.color_var,
            values=['blue', 'green', 'red', 'yellow', 'purple', 'orange']
        )
        self.color_combobox.pack()

        # キャンバスの設定
        self.canvas = Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack()

        # 画像をロードするボタンの設定
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()

        # 輪郭描画クラスの初期化
        self.drawer = None

        # Deleterクラスの初期化
        self.deleter = Deleter(self.canvas)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            original_img = Image.open(file_path)
            img = self.resize_image_to_canvas(original_img)
            self.img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.img)
            self.canvas.config(width=img.width, height=img.height)
            
            # 輪郭描画クラスを初期化してバインドを設定
            self.drawer = ContourDrawer(self.canvas, self.color_var, original_img.size)

    def resize_image_to_canvas(self, img):
        self.canvas.update()  # キャンバスのサイズを更新
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
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
