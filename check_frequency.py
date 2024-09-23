import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2

# フーリエ変換後の画像にハイパスフィルタを適用する関数（中心に黒い円を付ける）
def apply_circular_highpass_filter(fft_image, radius):
    # フーリエスペクトルのサイズ
    rows, cols = fft_image.shape
    crow, ccol = rows // 2, cols // 2  # 中心座標

    # 円形マスクの作成
    y, x = np.ogrid[:rows, :cols]
    mask_area = (x - ccol) ** 2 + (y - crow) ** 2 >= radius ** 2
    highpass_mask = mask_area.astype(float)  # マスクを1と0で表現

    # フーリエ変換結果にマスクを適用（低周波成分を除去）
    filtered_fft_image = fft_image * highpass_mask

    return filtered_fft_image

# 画像の高周波成分量を計算し、ハイパスフィルタ後のスペクトル画像を返す関数
def calculate_high_frequency_energy_with_filter(image, radius):
    # 画像をグレースケールに変換
    gray_image = image.convert("L")
    img_array = np.array(gray_image, dtype=np.float64)

    # フーリエ変換
    fft_image = np.fft.fftshift(np.fft.fft2(img_array))
    h, w = fft_image.shape[:2]
    print(np.sum(np.abs(fft_image[h//2-30:h//2+30, w//2-30:w//2+30]) ** 2))
    # ハイパスフィルタを適用（中心に黒い円を付ける）
    filtered_fft_image = apply_circular_highpass_filter(fft_image, radius)

    # 高周波成分のエネルギー量を計算（振幅の二乗の総和）
    high_freq_energy = np.sum(np.abs(filtered_fft_image) ** 2)

    # フィルタ後のフーリエスペクトルの振幅を取得（可視化用）
    amplitude_spectrum = np.log(np.abs(filtered_fft_image) + 1)  # 振幅のログスケールで表示

    return high_freq_energy, amplitude_spectrum

# ハイパスフィルタ付きで2つの画像を比較する関数
def compare_two_images_with_highpass_filter(image_path1, image_path2, radius):
    # 画像1を読み込む
    image1 = Image.open(image_path1)
    # 画像2を読み込む
    image2 = Image.open(image_path2)

    # 画像1の高周波成分量とハイパスフィルタ後のスペクトルを計算
    energy1, spectrum1 = calculate_high_frequency_energy_with_filter(image1, radius)

    # 画像2の高周波成分量とハイパスフィルタ後のスペクトルを計算
    energy2, spectrum2 = calculate_high_frequency_energy_with_filter(image2, radius)

    # 結果を出力
    print(f"画像1: 高周波エネルギー = {energy1:.1E}")
    print(f"画像2: 高周波エネルギー = {energy2:.1E}")

    # 結果をグラフで表示
    plt.figure(figsize=(10, 6))

    # 画像1とスペクトル表示
    plt.subplot(2, 2, 1)
    plt.imshow(image1, cmap='gray')
    plt.title("画像1")

    plt.subplot(2, 2, 2)
    plt.imshow(spectrum1, cmap='gray')
    plt.title(f"画像1のスペクトル (ハイパス, r={radius})")

    # 画像2とスペクトル表示
    plt.subplot(2, 2, 3)
    plt.imshow(image2, cmap='gray')
    plt.title("画像2")

    plt.subplot(2, 2, 4)
    plt.imshow(spectrum2, cmap='gray')
    plt.title(f"画像2のスペクトル (ハイパス, r={radius})")

    plt.tight_layout()
    plt.show()

    # 高周波エネルギーの比較
    if energy1 > energy2:
        print("画像1の高周波成分のエネルギーが大きいです。")
    elif energy1 < energy2:
        print("画像2の高周波成分のエネルギーが大きいです。")
    else:
        print("両方の画像の高周波成分のエネルギーは同じです。")

# 使用例: 2つの画像ファイルのパスと円の半径を指定してください
if __name__ == "__main__":
    image_path1 = r'C:\Users\pshun\Documents\python\tkinter_killingtime\P1180334.JPG'  # ここに1つ目の画像ファイルのパスを指定
    image_path2 = r'C:\Users\pshun\Documents\python\tkinter_killingtime\PB050070_01.jpg'  # ここに2つ目の画像ファイルのパスを指定
    radius = 30  # ハイパスフィルタの円の半径
    compare_two_images_with_highpass_filter(image_path1, image_path2, radius)
