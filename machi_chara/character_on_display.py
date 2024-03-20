import tkinter as tk
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.tk_color import rgb_code2rgb
from util.mask_greenback import get_mask
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

        # ウィンドウを閉じるためのキーバインディングを追加
        self.root.bind('<Escape>', self.close_window)


        # 動画を読み込む
        self.video = cv2.VideoCapture(video_path)

        self.window_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH) * r)
        self.window_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT) * r)

        self.monitor_index = monitor_index
        self.select_monitor(self.monitor_index)
        #self.root.geometry(f"{self.window_width}x{self.window_height}")

        # window direction (1:right, -1:left)
        self.move_angular = np.random.randint(0, 360)*np.pi/360
        self.direction_x = 1 if np.cos(self.move_angular) >= 0 else -1
        self.direction_y = 1 if np.sin(self.move_angular) >= 0 else -1
        
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

        # ウィンドウの位置を計算（端で起動すると角度計算が面倒なので上下左右1ピクセルずつマージンを設けている）
        self.x = -self.screen_width * monitor_index + np.random.randint(1, self.screen_width - self.window_width - 1) # initial
        self.y = np.random.randint(1, self.screen_height - self.window_height - 1) # initial

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

    def move_window(self, step):
        # ウィンドウの移動方向を考慮して新しい位置を計算
        self.x += int(step*np.cos(self.move_angular))
        self.y += int(step*np.sin(self.move_angular))
        # 右端または左端に到達した場合は方向を反転
        if self.x + self.screen_width * self.monitor_index >= self.screen_width - self.window_width:
            self.move_angular = np.random.randint(0, 180)*np.pi/360 + np.pi/2
            self.direction_x = 1 if np.cos(self.move_angular) >= 0 else -1
            self.direction_y = 1 if np.sin(self.move_angular) >= 0 else -1
        elif self.x + self.screen_width * self.monitor_index <= 0:
            self.move_angular = np.random.randint(0, 180)*np.pi/360 - np.pi/2
            self.direction_x = 1 if np.cos(self.move_angular) >= 0 else -1
            self.direction_y = 1 if np.sin(self.move_angular) >= 0 else -1 
        if self.y >= self.screen_height - self.window_height:
            self.move_angular = np.random.randint(0, 180)*np.pi/360 + np.pi
            self.direction_x = 1 if np.cos(self.move_angular) >= 0 else -1
            self.direction_y = 1 if np.sin(self.move_angular) >= 0 else -1
        elif self.y <= 0:
            self.move_angular = np.random.randint(0, 180)*np.pi/360
            self.direction_x = 1 if np.cos(self.move_angular) >= 0 else -1
            self.direction_y = 1 if np.sin(self.move_angular) >= 0 else -1
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
    CharacterOnDisplayApp(fr"{image_dirpath}\ms_minutes_walking_GB.mp4", r=0.5, monitor_index=1)