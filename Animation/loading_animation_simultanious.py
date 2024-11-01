import tkinter as tk
import math
import threading
import time

# Gaussian Wave Interference Animation
def show_gaussian_wave_interference_animation(canvas, line_length, amplitude, frequency, speed, sigma):
    # 直線の中央を基点として配置
    start_x = 70
    end_x = start_x + line_length
    y_center = 150  # 画面の中央の高さ
    points = []  # 直線の各ポイント

    # 線を描画する初期ポイントを設定
    num_points = 250  # ポイントの数
    step = line_length / num_points

    # 初期位置に直線を描画（水平な線）
    for i in range(num_points + 1):
        x = start_x + i * step
        points.append((x, y_center))
    
    # 線を描画
    line = canvas.create_line(points, fill="white", width=2)

    # ガウシアン関数の定義
    def gaussian(x, mu, sigma):
        return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

    # 波の振動をアニメーション
    def animate_wave(t=0):
        new_points = []
        for i, (x, _) in enumerate(points):
            # 左からの波と右からの波の干渉
            offset_left = math.sin((x - start_x) * frequency + t * speed) * amplitude * gaussian(x, (start_x + (t * 5 * speed + (end_x - start_x) / 2) % (end_x - start_x + 1 + 2 * 3 * sigma) - 3 * sigma), sigma)
            offset_right = math.sin((end_x - x) * frequency + t * speed) * amplitude * gaussian(x, (end_x - ((t * 5 * speed + (end_x - start_x) / 2) % (end_x - start_x + 1 + 2 * 3 * sigma)) + 3 * sigma), sigma)
            combined_offset = offset_left + offset_right
            new_y = y_center + combined_offset
            new_points.append((x, new_y))
        
        # 直線を更新
        canvas.coords(line, *sum(new_points, ()))

        # 次のフレームを呼び出し
        canvas.after(50, animate_wave, t + 1)

    animate_wave()  # アニメーション開始

# Loading Window class
class LoadingWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Window setup
        self.title("Loading...")
        self.geometry("600x300")
        self.configure(bg='black')

        # Create canvas for animation
        self.canvas = tk.Canvas(self, width=600, height=300, bg='black')
        self.canvas.pack()

        # Start Gaussian animation
        show_gaussian_wave_interference_animation(self.canvas, line_length=500, amplitude=60, frequency=0.25, speed=0.3, sigma=70)

    # 閉じる処理
    def close_loading_window(self):
        self.destroy()

# Main Application class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up main window
        self.title("Main Application Window")
        self.geometry("600x400")

        # Countdown label
        self.count_label = tk.Label(self, text="Countdown: 10", font=("Arial", 24))
        self.count_label.pack(pady=50)

        # Start loading window in a new thread
        threading.Thread(target=self.show_loading_window).start()

        # Start countdown in main thread
        threading.Thread(target=self.countdown).start()

    # Show loading window in a separate thread
    def show_loading_window(self):
        self.loading_window = LoadingWindow(self)
        self.loading_window.mainloop()

    # Countdown in main window
    def countdown(self):
        for i in range(10, 0, -1):
            self.count_label.config(text=f"Countdown: {i}")
            print(f"count: {i}")
            time.sleep(1)  # 1秒待機

        # After 10 seconds, close loading window
        self.close_loading_window()

    # Close the loading window
    def close_loading_window(self):
        if self.loading_window:
            self.loading_window.close_loading_window()

# Start the application
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
