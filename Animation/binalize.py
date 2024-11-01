import cv2
import os

path = r"C:\Users\pshun\Documents\python\tkinter_killingtime\niwatori.jpg"
im = cv2.imread(path)

im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

th, im_gray_th_otsu = cv2.threshold(im_gray, 128, 255, cv2.THRESH_OTSU)

print(th)
# 117.0

cv2.imwrite(f'{os.path.dirname(__file__)}/test.png', im_gray_th_otsu)