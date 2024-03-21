import tkinter as tk
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.tk_color import rgb_code2rgb
from util.mask_greenback import get_mask
from util.tk_color import rgb_code2rgb
import cv2
import numpy as np
from PIL import Image, ImageTk
import time

time_measure = False

class CharacterOnDisplayApp:
    BG_COLOR = "#0000FF"

    def __init__(self, video_path, r = 1.0, monitor_index = 0):
        self.root = tk.Tk()
        # ウィンドウを全画面に設定
        self.root.attributes("-topmost", True)
        self.root.config(bg = self.BG_COLOR)
        # ウィンドウの背景を透明に設定
        #self.root.attributes('-alpha', 1.0)  # 透明度を1.0に設定（不透明）
        self.root.wm_overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", self.BG_COLOR)
        # 透明な背景を持つキャンバスを作成
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.bind('<Button-1>', self.close_window)
        self.canvas.pack(fill='both', expand=True)
        
        # window direction (1:right, -1:left)
        self.direction_x = 1
        self.direction_y = 1
        #self.move_angular = np.random.randint(270, 360)*np.pi/180
        self.moved_distance_x = 0
        self.moved_distance_y = 0

        # ウィンドウを閉じるためのキーバインディングを追加
        self.root.bind('<Escape>', self.close_window)


        # 動画を読み込む
        self.video = cv2.VideoCapture(video_path)

        self.window_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH) * r)
        self.window_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT) * r)

        self.select_monitor(monitor_index)
        #self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # 動画からフレーム数を取得する
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        # 動画のFPS（フレームレート）を取得する
        self.fps = int(self.video.get(cv2.CAP_PROP_FPS))

        self.update_frame()  # フレームを更新する関数を呼び出し

        self.root.mainloop()
        

    def close_window(self, event):
        self.root.destroy()

    def select_monitor(self, monitor_index):
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        if monitor_index < 0:
            return  # インデックスが負の場合はデフォルトのモニターに表示

        # モニターの解像度を取得
        monitor_width = self.screen_width
        monitor_height = self.screen_height

        # ウィンドウの位置を計算
        self.x = -monitor_width * monitor_index # initial
        self.y = 0  # initial ウィンドウを上端に表示する場合

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

    def move_window(self, step):
        width, height = self.root.winfo_width(), self.root.winfo_height()
        # ウィンドウの移動方向を考慮して新しい位置を計算
        self.x += self.direction_x * step
        self.y += self.direction_y * step
        self.moved_distance_x += step
        self.moved_distance_y += step
        # 右端または左端に到達した場合は方向を反転
        if self.moved_distance_x >= self.screen_width - self.window_width:
            self.direction_x *= -1
            self.moved_distance_x = 0
        if self.moved_distance_y >= self.screen_height - self.window_height:
            self.direction_y *= -1
            self.moved_distance_y = 0
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
    
    def update_frame(self):
        ret, frame = self.video.read()
        if ret:
            if time_measure:
                start = time.perf_counter()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 画像をリサイズ
            frame = cv2.resize(frame, (self.window_width, self.window_height), interpolation=cv2.INTER_LANCZOS4)
            frame[get_mask(frame)] = rgb_code2rgb(self.BG_COLOR)

            # 進行方向によって向きを変える
            if self.direction_x == -1:
                frame = np.array([i[::-1] for i in frame])
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # 以前の画像を削除
            self.canvas.delete("all")
            # キャンバス上に画像を描画
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            
            # 画像が参照され続けるようにラベルオブジェクトを保持
            self.canvas.imgtk = imgtk
            if time_measure:
                print(time.perf_counter() - start)
        else:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.canvas.after(10, self.update_frame)  # 10ミリ秒ごとにフレームを更新
        self.move_window(step = 5)

if __name__ == '__main__':
    image_dirpath = fr"{os.path.dirname(os.path.abspath(__file__))}/image"
    CharacterOnDisplayApp(fr"{image_dirpath}\ms_minutes_walking_GB - Made with Clipchamp.mp4", r=0.5, monitor_index=1)