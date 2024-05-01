import cv2
import numpy as np

def mosaic(img, alpha):
    h, w, ch = img.shape

    img = cv2.resize(img,(int(w*alpha), int(h*alpha)))
    img = cv2.resize(img,(w, h), interpolation=cv2.INTER_NEAREST)

    return img

img = cv2.imread(r"P1180312.JPG")

dst = mosaic(img, 0.02)
    
cv2.imwrite("output.png", dst)