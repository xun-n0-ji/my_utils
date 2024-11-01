import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk

# ウィンドウを初期化
root = tk.Tk()

# タスクバーの高さ（一般的に40ピクセル程度。環境によって異なるため、調整可能）
taskbar_height = 40

# モニターサイズを取得（ウィジェットバーを考慮）
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() - taskbar_height

# ウィンドウサイズを9割に設定
window_width = int(screen_width * 0.9)
window_height = int(screen_height * 0.9)

# ウィンドウの中央に表示するための位置を計算
position_x = int((screen_width - window_width) / 2)
position_y = int((screen_height - window_height) / 2)

# ウィンドウサイズと位置を設定
root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

# サイドバーの設定（幅はウィンドウの10%）
sidebar_width = int(window_width * 0.1)

# 左側フレームの設定（ウィンドウの50%の幅、ウィンドウ全体の高さ）
left_frame_width = int(window_width * 0.5)

# 右側フレームの設定（ウィンドウの40%の幅、ウィンドウ全体の高さ）
right_frame_width = int(window_width * 0.4)

# --- サイドバーを作成して左側に配置 ---
sidebar = tk.Frame(root, width=sidebar_width, height=window_height, bg="#2c3e50")  # ダークな背景色
sidebar.pack(side=tk.LEFT, fill="y")
sidebar.propagate(0)

# アイコンを作成 (仮の画像、ファイルが必要ならパスを指定)
image = Image.open(r"C:\Users\pshun\Documents\python\tkinter_killingtime\output.png")
image = image.resize((15, 15))
show_icon = ImageTk.PhotoImage(image)
#show_icon = PhotoImage(image, width=20, height=20)  # アイコン用の仮のイメージ
hide_icon = PhotoImage(width=20, height=20)

# サイドバーに表示・非表示ボタンを追加
toggle_button = tk.Button(sidebar, image=show_icon, text="Show/Hide", compound="left")
toggle_button.pack(pady=10)

# 線を描画するためのCanvasを追加
line_canvas = tk.Canvas(sidebar, width=sidebar_width, height=2, bg="#ffffff")  # 線のためのキャンバス
line_canvas.pack(pady=5)

# 線を描画
margin = sidebar_width * 0.05  # 5%のマージンを左右に追加
line_canvas.create_line(margin, 1, sidebar_width - margin, 1, fill="#ffffff")

# explanation_frame
explanation = tk.Label(sidebar, text = "widget",foreground="#ffffff", width=int(sidebar_width*0.8), height=5, bg="#2c3e50")  # ダークな背景色
explanation.pack()

# サイドバーに別のボタンを追加
button1 = tk.Button(sidebar, text="Button 1", bg="#34495e", fg="white")
button1.pack(pady=10)

button2 = tk.Button(sidebar, text="Button 2", bg="#34495e", fg="white")
button2.pack(pady=10)

# --- 左側のメインフレームを作成してサイドバーの右側に配置 ---
left_frame = tk.Frame(root, width=left_frame_width, height=window_height, bg="#1abc9c")  # 明るい緑色
left_frame.pack(side="left", fill="y")

# 左側フレーム内にCanvasを上部に配置
left_canvas = tk.Canvas(left_frame, width=left_frame_width, height=int(window_height * 0.3), bg="#16a085")  # 少し暗めの緑色
left_canvas.pack(side="top", fill="x")

# --- 右側のフレームを作成して左側フレームの右側に配置 ---
right_frame = tk.Frame(root, width=right_frame_width, height=window_height, bg="#e74c3c")  # 赤色
right_frame.pack(side="left", fill="y")

# 右側フレーム内にCanvasを上部に配置
right_canvas = tk.Canvas(right_frame, width=right_frame_width, height=int(window_height * 0.3), bg="#c0392b")  # 暗めの赤色
right_canvas.pack(side="top", fill="x")

# GUIを開始
root.mainloop()
