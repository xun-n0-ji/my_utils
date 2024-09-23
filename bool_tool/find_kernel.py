import cv2
import numpy as np

def calculate_difference(img1, img2):
    # 差分を計算してその合計値を返す
    difference = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    return difference

def find_optimal_blur(original_img, defocus_img):
    min_diff = float('inf')
    best_kernel_size = 1

    for kernel_size in range(1, 50, 2):  # 奇数サイズのカーネルでループ
        blurred_img = cv2.blur(original_img, (kernel_size, kernel_size))
        diff = calculate_difference(defocus_img, blurred_img)

        if diff < min_diff:
            min_diff = diff
            best_kernel_size = kernel_size

    return best_kernel_size
