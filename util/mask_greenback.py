import cv2
import numpy as np

# The video, edited with Clipchamp, features a green background with the RGB value of [95, 241, 17], as well as variations around it
# Some pixels exhibit fluctuations around their values, having different values

def get_mask(image):
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Specify the range of green hue
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    # Perform thresholding to detect the region of the green background
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # denoise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    image_mask = (mask == 255)
    
    return image_mask

def image_cnv(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    print(image)