import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
import threading
import math
import time

class ImageProcessor:
    def __init__(self, canvas, animation):
        self.canvas = canvas
        self.animation = animation
        self.image = None  # 元画像
        self.canvas_image = None  # 表示用画像
        self.image_id = None

    def open_image(self):
        # ファイルダイアログで画像を開く
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image = Image.open(file_path)
            self.canvas_image = self.image
            self.update_image()

    def update_image(self):
        # Canvasに画像を更新
        if self.canvas_image:
            photo = ImageTk.PhotoImage(self.canvas_image)
            if self.image_id is None:
                self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            else:
                self.canvas.itemconfig(self.image_id, image=photo)
            self.canvas.photo = photo  # ガベージコレクション対策

    def process_image(self):
        if self.image is None:
            print("No image loaded.")
            return

        # アニメーションとオーバーレイを表示
        self.animation.start()

        # 擬似処理
        def processing():
            time.sleep(5)  # 処理時間
            # 画像をぼかす
            self.canvas_image = self.image.filter(ImageFilter.BLUR)
            self.update_image()  # Canvasを更新
            self.animation.stop()  # アニメーション停止

        threading.Thread(target=processing, daemon=True).start()

class LoadingAnimation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.circles = []
        self.num_circles = 8
        self.radius = 20
        self.circle_radius = 8
        self.angle_step = 360 / self.num_circles
        self.overlay_id = None  # オーバーレイのID
        self.running = False  # アニメーション状態

    def add_overlay(self):
        # 画像を暗くする半透明矩形を追加
        if self.overlay_id is None:
            self.overlay_id = self.canvas.create_rectangle(
                0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                fill="black", stipple="gray50"
            )

    def remove_overlay(self):
        # 暗くする矩形を削除
        if self.overlay_id is not None:
            self.canvas.delete(self.overlay_id)
            self.overlay_id = None

    def draw_circles(self):
        # アニメーション用の円をキャンバス中央に配置
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2

        for i in range(self.num_circles):
            angle = math.radians(i * self.angle_step)
            x = center_x + self.radius * math.cos(angle)
            y = center_y + self.radius * math.sin(angle)
            circle = self.canvas.create_oval(
                x - self.circle_radius, y - self.circle_radius,
                x + self.circle_radius, y + self.circle_radius,
                fill="white", outline="white"
            )
            self.circles.append(circle)

    def start(self):
        # アニメーションを開始
        self.add_overlay()
        self.running = True

        if not self.circles:
            self.draw_circles()

        def animate(step=0):
            if not self.running:
                # アニメーションを停止
                for circle in self.circles:
                    self.canvas.delete(circle)
                self.circles.clear()
                self.remove_overlay()
                return
            
            for i in range(self.num_circles):
                offset = (i + step) % self.num_circles
                color_intensity = int(255 * (offset / self.num_circles))
                color = f'#{color_intensity:02x}{255:02x}{255:02x}'
                self.canvas.itemconfig(self.circles[i], fill=color)

            self.canvas.after(100, animate, step + 1)

        animate()

    def stop(self):
        # アニメーション停止フラグを設定
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Processing Tool")
    
    # Canvas
    canvas = tk.Canvas(root, width=400, height=400, bg="gray")
    canvas.pack()

    # Classes
    animation = LoadingAnimation(canvas)
    image_processor = ImageProcessor(canvas, animation)

    # Buttons
    open_button = tk.Button(root, text="Open", command=image_processor.open_image)
    open_button.pack(side=tk.LEFT, padx=10, pady=10)

    process_button = tk.Button(root, text="Process", command=image_processor.process_image)
    process_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()
