import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import os

# グローバル変数
drawing = False  # 描画中かどうかのフラグ
start_point = None  # 描画開始点
contours = []  # 描画した輪郭のリスト (ID付き)
selected_contour_id = None  # 選択された輪郭のID
image = None  # OpenCVの画像
image_copy = None  # 描画用のコピー
output_dir = "label"  # ラベル保存先ディレクトリ

# ラベルフォルダ作成
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def save_label(image_name, contour_id, contour):
    """輪郭線の座標をファイルに保存"""
    label_path = os.path.join(output_dir, f"{image_name}.txt")
    with open(label_path, 'a') as f:
        coord_str = " ".join([f"{x} {y}" for x, y in contour])
        f.write(f"{contour_id} {coord_str}\n")

def delete_label(image_name, contour_id):
    """指定IDのラベルを削除"""
    label_path = os.path.join(output_dir, f"{image_name}.txt")
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            lines = f.readlines()
        with open(label_path, 'w') as f:
            for line in lines:
                if not line.startswith(f"{contour_id} "):
                    f.write(line)

def select_image():
    """画像を選択して表示"""
    global image, image_copy
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        image_copy = image.copy()
        cv2.imshow("Image", image_copy)
        cv2.setMouseCallback("Image", draw_contour)
        
        # 画像名を取得
        global image_name
        image_name = os.path.splitext(os.path.basename(file_path))[0]

def draw_contour(event, x, y, flags, param):
    """マウスイベントで輪郭を描画"""
    global drawing, start_point, image_copy, contours, selected_contour_id

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        selected_contour_id = None

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            image_copy = image.copy()
            cv2.rectangle(image_copy, start_point, (x, y), (255, 0, 0), 2)
            cv2.imshow("Image", image_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        contour = [start_point, (end_point[0], start_point[1]), end_point, (start_point[0], end_point[1])]
        contour_id = len(contours)
        contours.append((contour_id, contour))
        cv2.rectangle(image, start_point, end_point, (255, 0, 0), 2)
        cv2.imshow("Image", image)
        
        # 座標をラベルファイルに保存
        save_label(image_name, contour_id, contour)

    elif event == cv2.EVENT_RBUTTONDOWN:
        # クリックした位置にある輪郭を選択
        for contour_id, contour in contours:
            if cv2.pointPolygonTest(np.array(contour), (x, y), False) >= 0:
                selected_contour_id = contour_id
                # 輪郭を赤色に変更
                image_copy = image.copy()
                cv2.fillPoly(image_copy, [np.array(contour)], (0, 0, 255))
                cv2.imshow("Image", image_copy)
                break

def remove_selected_contour():
    """選択された輪郭を削除"""
    global contours, image

    if selected_contour_id is not None:
        # 輪郭をリストから削除
        contours = [c for c in contours if c[0] != selected_contour_id]
        
        # 画像から削除
        image = image_copy.copy()
        for contour_id, contour in contours:
            cv2.polylines(image, [np.array(contour)], True, (255, 0, 0), 2)
        cv2.imshow("Image", image)
        
        # ラベルファイルから削除
        delete_label(image_name, selected_contour_id)

def on_key_press(event):
    """キー入力イベント (sキーで輪郭削除)"""
    if event.char == 's' and selected_contour_id is not None:
        remove_selected_contour()

# Tkinterウィンドウのセットアップ
root = tk.Tk()
root.title("Image Annotation Tool")

# 画像選択ボタン
btn = tk.Button(root, text="Select Image", command=select_image)
btn.pack()

# キーボードイベントのバインド
root.bind('<KeyPress>', on_key_press)

root.mainloop()
