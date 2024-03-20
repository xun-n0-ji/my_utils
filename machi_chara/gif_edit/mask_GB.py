import cv2
import numpy as np

# video, which is editted with Clipchamp, has a green back with value of [r, g, b] = [95, 241, 17]

def get_mask(image):
    # HSVカラースペースに変換
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # グリーンの色相の範囲を指定
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # しきい値処理を行ってグリーンバックの領域を検出
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # ノイズを削除
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    image_mask = (mask == 255)
    
    return image_mask

def image_cnv(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    print(image)