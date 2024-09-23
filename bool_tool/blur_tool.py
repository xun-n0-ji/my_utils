import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageTk

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if file_path:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        process_image(img)

def process_image(img):
    global original_img
    original_img = img
    update_blur()

def update_blur(val=5):
    global original_img, blurred_img

    blur_value = int(blur_slider.get())
    if blur_value % 2 == 0:  # cv2.blur requires an odd kernel size
        blur_value += 1

    # Apply cv2.blur
    blurred_img = cv2.blur(original_img, (blur_value, blur_value))

    # Compute Fourier transform of both images
    fft_original = np.fft.fftshift(np.fft.fft2(original_img))
    magnitude_original = 20 * np.log(np.abs(fft_original) + 1)

    fft_blur = np.fft.fftshift(np.fft.fft2(blurred_img))
    magnitude_blur = 20 * np.log(np.abs(fft_blur) + 1)

    # Plot all 4 images (original, blurred, their Fourier transforms)
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    axes[0, 0].imshow(original_img, cmap='gray')
    axes[0, 0].set_title('Original Image')
    axes[0, 0].axis('off')

    axes[0, 1].imshow(blurred_img, cmap='gray')
    axes[0, 1].set_title(f'Blurred Image (kernel: {blur_value})')
    axes[0, 1].axis('off')

    axes[1, 0].imshow(magnitude_original, cmap='gray')
    axes[1, 0].set_title('FFT of Original Image')
    axes[1, 0].axis('off')

    axes[1, 1].imshow(magnitude_blur, cmap='gray')
    axes[1, 1].set_title('FFT of Blurred Image')
    axes[1, 1].axis('off')

    # Save the plot to a file
    plt.tight_layout()
    plt.savefig('result.png')
    plt.close()

    # Display the result on the GUI
    display_result('result.png')

def display_result(image_path):
    result_img = Image.open(image_path)
    result_img = ImageTk.PhotoImage(result_img)
    result_label.config(image=result_img)
    result_label.image = result_img

# Set up the Tkinter window
root = tk.Tk()
root.title("Image Blurring and Fourier Transform")

# Add button to open an image
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack()

# Add slider to adjust blur level
blur_slider = tk.Scale(root, from_=1, to=50, orient=tk.HORIZONTAL, label="Blur Amount", command=update_blur)
blur_slider.pack()

# Add label to display the result
result_label = tk.Label(root)
result_label.pack()

root.mainloop()
