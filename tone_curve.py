import cv2
import numpy as np

def apply_sin_curve(image):
    # 画像をグレースケールに変換
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 画像の高さと幅を取得
    height, width = gray_image.shape
    
    # 正弦波の周期と振幅を定義
    frequency = 5  # 周期
    amplitude = 255  # 振幅
    
    # LUTを作成
    lut = np.zeros(256, dtype=np.uint8)
    for i in range(256):
        lut[i] = np.clip(amplitude * np.sin(2 * np.pi * frequency * i / 255), 0, 255)
    
    # LUTを使って画像にトーンカーブを適用
    result_image = cv2.LUT(gray_image, lut)
    
    # グレースケール画像をカラー画像に変換
    result_image = cv2.cvtColor(result_image, cv2.COLOR_GRAY2BGR)
    
    return result_image

# 画像の読み込み
input_image = cv2.imread("PC210025.JPG")
height, width = input_image.shape[:2]
# 正弦波状のトーンカーブを適用
output_image = apply_sin_curve(input_image)

# 変換された画像を表示
cv2.imshow("Original Image", cv2.resize(input_image, (width//4, height//4)))
cv2.imshow("Sin Curve Image", cv2.resize(output_image, (width//4, height//4)))
cv2.waitKey(0)
cv2.destroyAllWindows()
