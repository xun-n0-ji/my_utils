import cv2
import numpy as np

# 画像の読み込み
image = cv2.imread('image.png')

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

# キャラクターの領域を抽出
#result = cv2.bitwise_and(image, image, mask=mask)
image[image_mask] = 0

# 結果を表示
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
