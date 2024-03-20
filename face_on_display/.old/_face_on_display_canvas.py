import tkinter as tk
import cv2
from PIL import Image, ImageTk
import time

class FaceOnDisplayApp:
    def __init__(self):
        self.root = tk.Tk()
        # ウィンドウを全画面に設定
        self.root.attributes('-fullscreen', True)

        # ウィンドウの背景を透明に設定
        self.root.attributes('-alpha', 0.5)  # 透明度を0.5に設定（0は完全透明、1は不透明）

        # 透明な背景を持つキャンバスを作成
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
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
            start = time.perf_counter()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.root.winfo_width(), self.root.winfo_height()))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # キャンバスに画像を描画
            self.canvas.delete("all")  # 以前の画像を削除
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.imgtk = imgtk  # 画像が参照され続けるようにラベルオブジェクトを保持

            print(time.perf_counter() - start)

        self.canvas.after(10, self.update_frame)  # 10ミリ秒ごとにフレームを更新

if __name__ == '__main__':
    FaceOnDisplayApp()
