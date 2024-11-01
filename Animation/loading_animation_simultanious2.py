import tkinter as tk
import math
import threading
import time

# Gaussian Wave Interference Animation
def show_gaussian_wave_interference_animation(canvas, line_length, amplitude, frequency, speed, sigma):
    start_x = 70
    end_x = start_x + line_length
    y_center = 150  # 画面の中央の高さ
    points = []  # 直線の各ポイント

    num_points = 250  # ポイントの数
    step = line_length / num_points

    for i in range(num_points + 1):
        x = start_x + i * step
        points.append((x, y_center))
    
    line = canvas.create_line(points, fill="white", width=2)

    def gaussian(x, mu, sigma):
        return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

    def animate_wave(t=0):
        new_points = []
        for i, (x, _) in enumerate(points):
            offset_left = math.sin((x - start_x) * frequency + t * speed) * amplitude * gaussian(x, (start_x + (t * 5 * speed + (end_x - start_x) / 2) % (end_x - start_x + 1 + 2 * 3 * sigma) - 3 * sigma), sigma)
            offset_right = math.sin((end_x - x) * frequency + t * speed) * amplitude * gaussian(x, (end_x - ((t * 5 * speed + (end_x - start_x) / 2) % (end_x - start_x + 1 + 2 * 3 * sigma)) + 3 * sigma), sigma)
            combined_offset = offset_left + offset_right
            new_y = y_center + combined_offset
            new_points.append((x, new_y))
        
        canvas.coords(line, *sum(new_points, ()))
        canvas.after(50, animate_wave, t + 1)

    animate_wave()

# LoadingWindowクラス
class LoadingWindow:
    def __init__(self, root):
        self.root = root
        self.loading_root = tk.Toplevel()
        self.loading_root.title("Loading...")
        self.loading_root.geometry("600x300")
        self.loading_root.configure(bg='black')
        self.canvas = tk.Canvas(self.loading_root, width=600, height=300, bg='black')
        self.canvas.pack()

    def close_loading(self):
        self.loading_root.destroy()
        self.root.deiconify()

    def start_loading(self):
        show_gaussian_wave_interference_animation(self.canvas, line_length=500, amplitude=60, frequency=0.25, speed=0.3, sigma=70)

# MainAppクラス
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Application Window")
        self.root.geometry("600x400")

        self.count_label = tk.Label(self.root, text="Start loading...", font=("Arial", 24))
        self.count_label.pack(pady=50)

        # ボタンで操作
        start_button = tk.Button(self.root, text="Start Task", command=self.start_long_task)
        start_button.pack(pady=10)

    # 時間がかかる処理の前にローディングウィンドウを表示
    def start_long_task(self):
        self.root.withdraw()
        # Loading windowの定義
        self.loading_window = LoadingWindow(self.root)
        # スレッドでローディングウィンドウを起動
        loading_thread = threading.Thread(target=self.run_task)
        loading_thread.start()

    # 実際のタスク処理
    def run_task(self):
        # ローディングウィンドウを表示
        self.root.after(0, self.loading_window.start_loading)

        # 長時間かかる処理をシミュレーション（例: 10秒カウントダウン）
        for i in range(10, 0, -1):
            time.sleep(1)  # 1秒待機
            print(f"count: {i}")
            self.root.after(0, self.update_countdown_label, f"Counting: {i}")

        # ローディングウィンドウを閉じる
        self.root.after(0, self.loading_window.close_loading)

    # カウントダウンラベルの更新
    def update_countdown_label(self, text):
        self.count_label.config(text=text)

# アプリケーションの開始
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
