import cv2
import numpy as np
from matplotlib import pyplot as plt

def compute_fft_magnitude(img):
    # フーリエ変換を行い、周波数成分を取得する
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
    return magnitude_spectrum

def calculate_fft_difference(img1, img2):
    # 2つの画像のフーリエ変換の差を計算する
    fft1 = compute_fft_magnitude(img1)
    fft2 = compute_fft_magnitude(img2)
    
    # フーリエ変換の差の絶対値を合計して返す
    difference = np.sum(np.abs(fft1 - fft2))
    return difference

def find_optimal_blur(original_img, defocus_img):
    min_diff = float('inf')
    best_kernel_size = 1

    for kernel_size in range(1, 50, 2):  # 奇数カーネルサイズでループ
        blurred_img = cv2.blur(original_img, (kernel_size, kernel_size))
        diff = calculate_fft_difference(defocus_img, blurred_img)

        if diff < min_diff:
            min_diff = diff
            best_kernel_size = kernel_size

        print(f'Kernel size: {kernel_size}, Difference: {diff}')
    
    return best_kernel_size

# 画像を読み込む（グレースケール）
original_img = cv2.imread('original_image.jpg', cv2.IMREAD_GRAYSCALE)
defocus_img = cv2.imread('defocus_image.jpg', cv2.IMREAD_GRAYSCALE)

# 最適なカーネルサイズを見つける
best_kernel_size = find_optimal_blur(original_img, defocus_img)
print(f'Optimal kernel size: {best_kernel_size}')

# 見つけたカーネルサイズでblurを適用
optimal_blurred_img = cv2.blur(original_img, (best_kernel_size, best_kernel_size))

# 結果を表示
plt.subplot(131), plt.imshow(original_img, cmap='gray')
plt.title('Original Image'), plt.axis('off')

plt.subplot(132), plt.imshow(defocus_img, cmap='gray')
plt.title('Defocus Image'), plt.axis('off')

plt.subplot(133), plt.imshow(optimal_blurred_img, cmap='gray')
plt.title(f'Blurred Image (kernel: {best_kernel_size})'), plt.axis('off')

plt.show()
