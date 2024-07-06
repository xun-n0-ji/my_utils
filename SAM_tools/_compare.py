import cv2
import numpy as np
import time

def find_contours_direct(mask):
    start_time = time.perf_counter()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    end_time = time.perf_counter()
    return contours, end_time - start_time

def find_contours_erode_difference(mask):
    start_time = time.perf_counter()
    eroded_mask = cv2.erode(mask, np.ones((3, 3), np.uint8))
    diff_mask = cv2.absdiff(mask, eroded_mask)
    contours, _ = cv2.findContours(diff_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    end_time = time.perf_counter()
    return contours, end_time - start_time

# 入力画像、マスク画像のパスを指定
mask_image_path = r'C:\Users\pshun\Documents\python\tkinter_killingtime\SAM_tools\mask.png'

# マスク画像を読み込む
mask = cv2.imread(mask_image_path, cv2.IMREAD_GRAYSCALE)

# 方法1: cv2.findContoursを直接使用
contours_direct, time_direct = find_contours_direct(mask)

# 方法2: cv2.erodeと差分を使用
contours_erode, time_erode = find_contours_erode_difference(mask)

print(f"findContours direct method time: {time_direct:.12f} seconds")
print(f"Erode and difference method time: {time_erode:.12f} seconds")

# 速度比較結果の表示
if time_direct < time_erode:
    print("cv2.findContours direct method is faster.")
else:
    print("Erode and difference method is faster.")
