import cv2
import numpy as np

def apply_sin_curve(image, frequencies, amplitudes):
    # 各チャンネルごとにトーンカーブを適用
    result_channels = []
    for ch in range(image.shape[2]):
        # LUTを作成
        lut = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            lut[i] = np.clip(amplitudes[ch] * np.sin(2 * np.pi * frequencies[ch] * i / 255), 0, 255)
        # LUTを使って画像にトーンカーブを適用
        result_channels.append(cv2.LUT(image[:, :, ch], lut))
    
    # 各チャンネルを結合して結果の画像を作成
    result_image = np.stack(result_channels, axis=2)
    
    return result_image

# 画像の読み込み
input_image = cv2.imread("PC210025.JPG")
height, width = input_image.shape[:2]

# 各チャンネルごとの周波数と振幅を設定
frequencies = [2, 2, 2]  # 各チャンネルの周波数
amplitudes = [255, 255, 255]   # 各チャンネルの振幅

# 正弦波状のトーンカーブを適用
output_image = apply_sin_curve(input_image, frequencies, amplitudes)

# 変換された画像を表示
cv2.imshow("Original Image", cv2.resize(input_image, (width//4, height//4)))
cv2.imshow("Sin Curve Image", cv2.resize(output_image, (width//4, height//4)))
cv2.waitKey(0)
cv2.destroyAllWindows()

import matplotlib.pyplot as plt

def generate_sin_curve(frequency, amplitude):
    x = np.linspace(0, 255, 256)
    y = amplitude * np.sin(2 * np.pi * frequency * x / 255)
    return x, y

for ch in range(len(frequencies)):
    frequency = frequencies[ch]
    amplitude = amplitudes[ch]
    x, y = generate_sin_curve(frequency, amplitude)
    plt.plot(x, y, label=f"Channel {ch+1}: Freq={frequency}, Amp={amplitude}")

plt.title("Sin Curve Tone Mapping")
plt.xlabel("Input Intensity")
plt.ylabel("Output Intensity")
plt.legend()
plt.grid(True)
plt.show()
