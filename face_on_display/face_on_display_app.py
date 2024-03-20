from depth_estimation import DepthEstimation
import tkinter as tk
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.tk_color import rgb_code2rgb
import cv2
import numpy as np
from PIL import Image, ImageTk
import time

time_measure = False

class FaceOnDisplayApp:
    BG_COLOR = "#0000FF"

    def __init__(self):
        self.root = tk.Tk()
        # ウィンドウを全画面に設定
        self.root.attributes('-fullscreen', True)
        self.root.config(bg = self.BG_COLOR)
        # ウィンドウの背景を透明に設定
        #self.root.attributes('-alpha', 1.0)  # 透明度を1.0に設定（不透明）
        self.root.wm_overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", self.BG_COLOR)
        # 透明な背景を持つキャンバスを作成
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        # ウィンドウを閉じるためのキーバインディングを追加
        self.root.bind('<Escape>', self.close_window)

        # カメラのキャプチャを開始
        self.cap = cv2.VideoCapture(0)

        self.update_frame()  # フレームを更新する関数を呼び出し

        self.root.mainloop()

    def close_window(self, event):
        self.root.destroy()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            if time_measure:
                start = time.perf_counter()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ウィンドウのサイズを取得
            window_width = self.root.winfo_screenwidth()
            window_height = self.root.winfo_screenheight()

            # 画像のサイズを取得
            image_height, image_width, _ = frame.shape

            # ウィンドウのアスペクト比を計算
            window_aspect_ratio = window_width / window_height

            # 画像のアスペクト比を計算
            image_aspect_ratio = image_width / image_height

            if window_aspect_ratio > image_aspect_ratio:
                # ウィンドウのアスペクト比が画像のアスペクト比より大きい場合、ウィンドウの高さを画像の高さに合わせる
                display_height = window_height
                display_width = int(window_height * image_aspect_ratio)
            else:
                # 画像のアスペクト比がウィンドウのアスペクト比より大きい場合、ウィンドウの幅を画像の幅に合わせる
                display_width = window_width
                display_height = int(window_width / image_aspect_ratio)

            # 画像をリサイズ
            frame = cv2.resize(frame, (display_width, display_height))

            # 深度推定画像に変換
            depth_estimated_mask = DepthEstimation().get_estimate_depth_mask(frame, 190)
            frame[np.logical_not(depth_estimated_mask)] = rgb_code2rgb(self.BG_COLOR)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # 以前の画像を削除
            self.canvas.delete("all")
            # キャンバス上に画像を描画
            self.canvas.create_image((window_width - display_width) // 2, (window_height - display_height) // 2, anchor="nw", image=imgtk)
            
            # 画像が参照され続けるようにラベルオブジェクトを保持
            self.canvas.imgtk = imgtk
            if time_measure:
                print(time.perf_counter() - start)

        self.canvas.after(10, self.update_frame)  # 10ミリ秒ごとにフレームを更新

if __name__ == '__main__':
    FaceOnDisplayApp()