import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
import threading
import math
import time

class ImageProcessor:
    def __init__(self, canvas):
        self.canvas = canvas
        self.image = None
        self.photo = None
        self.image_id = None
        self.overlay_id = None  # 暗くするための矩形のID

    def open_image(self):
        # ファイルダイアログで画像を開く
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)

    def display_image(self, image):
        # Canvasに画像を表示
        self.photo = ImageTk.PhotoImage(image)
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        else:
            self.canvas.itemconfig(self.image_id, image=self.photo)

    def add_overlay(self):
        # 画像を暗くする半透明矩形を追加
        if self.overlay_id is None:
            self.overlay_id = self.canvas.create_rectangle(
                0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                fill="black", stipple="gray50"  # 半透明黒
            )

    def remove_overlay(self):
        # 暗くする矩形を削除
        if self.overlay_id is not None:
            self.canvas.delete(self.overlay_id)
            self.overlay_id = None

    def process_image(self, animation):
        if self.image is None:
            print("No image loaded.")
            return
        
        # 暗くするオーバーレイを表示
        self.add_overlay()
        
        # アニメーション開始
        stop_event = threading.Event()
        threading.Thread(target=animation.start, args=(stop_event,), daemon=True).start()

        # 擬似処理
        def processing():
            time.sleep(5)  # 処理時間
            # 画像をぼかす
            blurred_image = self.image.filter(ImageFilter.BLUR)
            self.display_image(blurred_image)
            stop_event.set()  # アニメーション停止
            self.remove_overlay()  # 暗いオーバーレイを削除
        
        threading.Thread(target=processing, daemon=True).start()

class LoadingAnimation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.circles = []
        self.num_circles = 8
        self.radius = 20
        self.circle_radius = 8
        self.angle_step = 360 / self.num_circles

    def draw_circles(self):
        # アニメーション用の円を作成
        for i in range(self.num_circles):
            angle = math.radians(i * self.angle_step)
            x = 100 + self.radius * math.cos(angle)
            y = 100 + self.radius * math.sin(angle)
            circle = self.canvas.create_oval(
                x - self.circle_radius, y - self.circle_radius,
                x + self.circle_radius, y + self.circle_radius,
                fill="white", outline="white"
            )
            self.circles.append(circle)

    def start(self, stop_event):
        # アニメーションを開始
        if not self.circles:
            self.draw_circles()

        def animate(step=0):
            if stop_event.is_set():
                # アニメーションを停止
                for circle in self.circles:
                    self.canvas.delete(circle)
                self.circles.clear()
                return
            
            for i in range(self.num_circles):
                offset = (i + step) % self.num_circles
                color_intensity = int(255 * (offset / self.num_circles))
                color = f'#{color_intensity:02x}{255:02x}{255:02x}'
                self.canvas.itemconfig(self.circles[i], fill=color)

            self.canvas.after(100, animate, step + 1)

        animate()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Processing Tool")
    
    # Canvas
    canvas = tk.Canvas(root, width=400, height=400, bg="gray")
    canvas.pack()

    # Classes
    image_processor = ImageProcessor(canvas)
    animation = LoadingAnimation(canvas)

    # Buttons
    open_button = tk.Button(root, text="Open", command=image_processor.open_image)
    open_button.pack(side=tk.LEFT, padx=10, pady=10)

    process_button = tk.Button(root, text="Process", command=lambda: image_processor.process_image(animation))
    process_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()
