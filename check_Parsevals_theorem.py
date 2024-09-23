import numpy as np
from PIL import Image
import random

# 画像のフーリエエネルギーの平方根を計算する関数
def calc_fourier_energy_sqrt(image):
    # 画像をグレースケールに変換
    gray_image = image.convert("L")
    # 画像をnumpy配列に変換
    img_array = np.array(gray_image, dtype=np.float64)
    # フーリエ変換を実行
    fft = np.fft.fft2(img_array)
    # フーリエエネルギーを計算（パーセバルの定理に基づく）
    energy = np.sum(np.abs(fft)**2)
    # エネルギーの平方根
    return np.sqrt(energy)

# 画像をl, mにランダムに分割し、フーリエエネルギーの平方根を計算する関数
def split_and_compare_fourier_energy(image_path):
    # 画像を読み込む
    image = Image.open(image_path)
    width, height = image.size

    # 水平方向と垂直方向の分割数をランダムに決定
    l = random.randint(2, 5)
    m = random.randint(2, 5)
    print(f"分割数: 水平方向 {l} 個, 垂直方向 {m} 個")

    # 各分割のランダムなスパンを計算
    # 水平方向の分割位置をランダムに選択
    x_split_points = sorted(random.sample(range(1, width), l - 1))
    x_splits = [0] + x_split_points + [width]
    # 垂直方向の分割位置をランダムに選択
    y_split_points = sorted(random.sample(range(1, height), m - 1))
    y_splits = [0] + y_split_points + [height]

    # 元の画像のフーリエエネルギーの平方根を計算
    original_energy_sqrt = calc_fourier_energy_sqrt(image)
    print(f"元の画像のフーリエエネルギーの平方根: {original_energy_sqrt:.1E}")

    # 分割された画像のフーリエエネルギーの平方根の和を計算
    total_split_energy_sqrt = 0
    for i in range(l):
        for j in range(m):
            left = x_splits[i]
            right = x_splits[i + 1]
            upper = y_splits[j]
            lower = y_splits[j + 1]

            # 各分割領域を切り出し
            cropped_image = image.crop((left, upper, right, lower))
            # 分割画像のフーリエエネルギーの平方根を計算
            split_energy_sqrt = calc_fourier_energy_sqrt(cropped_image)
            total_split_energy_sqrt += split_energy_sqrt

    print(f"分割した画像のフーリエエネルギーの平方根の和: {total_split_energy_sqrt:.1E}")

    # 比較
    if np.isclose(original_energy_sqrt, total_split_energy_sqrt, rtol=1e-5):
        print("元の画像と分割画像のフーリエエネルギーの平方根はほぼ同じです。")
    else:
        print("元の画像と分割画像のフーリエエネルギーの平方根は異なります。")

# 使用例: 画像ファイルのパスを指定してください
if __name__ == "__main__":
    image_path = r'C:\Users\pshun\Documents\python\tkinter_killingtime\thumbnail_zukei.jpg'  # ここに対象の画像ファイルパスを入力してください
    split_and_compare_fourier_energy(image_path)
