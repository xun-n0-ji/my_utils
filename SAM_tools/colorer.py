import cv2
import numpy as np
import os

# 入力画像、マスク画像、出力画像のパスを指定
input_image_path = r'C:\Users\pshun\Documents\python\tkinter_killingtime\niwatori.jpg'
mask_image_path = r'C:\Users\pshun\Documents\python\tkinter_killingtime\SAM_tools\mask.png'
output_image_path = os.path.join(os.path.dirname(__file__), "color.png")

image = cv2.imread(input_image_path)
mask = cv2.imread(mask_image_path, cv2.IMREAD_GRAYSCALE)

def apply_mask(image, mask, color):
    # 輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭を赤色で描画
    cv2.drawContours(image, contours, -1, color, 1)

    # マスクの内側を薄赤く色付け
    overlay = image.copy()
    for contour in contours:
        cv2.drawContours(overlay, [contour], -1, color, -1)

    # 透過効果を適用
    alpha = 0.2  # 透過度
    overlayed_image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    return overlayed_image

overlayed_image = apply_mask(image, mask, (255, 0, 0))

# 結果を保存
cv2.imwrite(output_image_path, overlayed_image)

# マスク適用関数を呼び出し
#apply_mask(input_image_path, mask_image_path, output_image_path)
