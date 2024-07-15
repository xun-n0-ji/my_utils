import cv2
from rembg import remove
from PIL import Image, ImageTk
import numpy as np
import os
import tkinter as tk

class ImageProcessor:
    def __init__(self):
        pass

    def remove_background(self, input_image_path, output_image_path):
        try:
            input_image = Image.open(input_image_path)
        except IOError:
            print(f"Error: Cannot open {input_image_path}")
            return False

        output_image = remove(input_image)
        output_image.save(output_image_path)
        return True

    def apply_mask_to_background(self, masked_image_path):
        rgba_image = cv2.imread(masked_image_path, cv2.IMREAD_UNCHANGED)
        if rgba_image is None:
            print(f"Error: Cannot open {masked_image_path}")
            return None

        alpha_channel = rgba_image[:, :, 3]
        mask = np.zeros_like(alpha_channel, dtype=np.uint8)
        mask[alpha_channel > 0] = 255
        
        return mask

class AnnotationManager:
    def __init__(self, output_dir, class_id):
        self.output_dir = output_dir
        self.class_id = class_id
        self.labels = []

    def save_contours_and_labels(self, mask, contours, image_path):
        label_path = f"{os.path.splitext(image_path)[0]}.txt"
        
        with open(label_path, 'w') as label_file:
            for idx, contour in enumerate(contours):
                contour_mask = np.zeros_like(mask, dtype=np.uint8)
                cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)
                
                contour_image_path = f"{os.path.splitext(image_path)[0]}_classID{self.class_id}_{idx}.png"
                cv2.imwrite(os.path.join(self.output_dir, contour_image_path), contour_mask)
                
                contour_points = contour.flatten().tolist()
                label_file.write(f"{self.class_id} " + " ".join(map(str, contour_points)) + "\n")
                self.labels.append((contour_image_path, contour_points))

    def delete_contour(self, idx, image_path):
        label_path = f"{os.path.splitext(image_path)[0]}.txt"
        if idx < len(self.labels):
            contour_image_path, _ = self.labels.pop(idx)
            if os.path.exists(os.path.join(self.output_dir, contour_image_path)):
                os.remove(os.path.join(self.output_dir, contour_image_path))
            with open(label_path, 'w') as label_file:
                for _, points in self.labels:
                    label_file.write(f"{self.class_id} " + " ".join(map(str, points)) + "\n")

class Deleter(tk.Canvas):
    def __init__(self, root, input_image_path, mask, contours, output_dir, class_id):
        super().__init__(root, width=mask.shape[1], height=mask.shape[0])
        self.root = root
        self.input_image_path = input_image_path
        self.mask = mask
        self.contours = list(contours)  # Convert tuple to list
        self.output_dir = output_dir
        self.class_id = class_id
        self.selected_contour_idx = None

        self.processor = ImageProcessor()
        self.manager = AnnotationManager(output_dir, class_id)
        
        self.root.title("Image with Mask")
        self.root.bind('<Delete>', self.on_delete)

        self.input_image = cv2.imread(input_image_path)
        self.input_image_rgb = cv2.cvtColor(self.input_image, cv2.COLOR_BGR2RGB)
        
        self.mask_colored = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
        self.alpha = 0.5
        self.overlay_image = cv2.addWeighted(self.input_image_rgb, 1 - self.alpha, self.mask_colored, self.alpha, 0)
        self.display_image = self.overlay_image.copy()

        self.image_pil = Image.fromarray(self.display_image)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        
        self.pack()
        self.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.image_tk = self.image_tk

        self.bind('<Motion>', self.on_mouse_move)
        self.bind('<Button-1>', self.on_mouse_click)

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        self.display_image = self.overlay_image.copy()
        self.selected_contour_idx = None
        for idx, contour in enumerate(self.contours):
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                self.selected_contour_idx = idx
                cv2.drawContours(self.display_image, [contour], -1, (0, 0, 255), thickness=2)
                break
        self.update_image(self.display_image)

    def on_mouse_click(self, event):
        if self.selected_contour_idx is not None:
            cv2.drawContours(self.overlay_image, [self.contours[self.selected_contour_idx]], -1, (0, 0, 255), thickness=cv2.FILLED)
            self.display_image = self.overlay_image.copy()
            self.update_image(self.display_image)

    def on_delete(self, event):
        if self.selected_contour_idx is not None:
            contour_to_delete = self.contours.pop(self.selected_contour_idx)
            cv2.drawContours(self.mask, [contour_to_delete], -1, 0, thickness=cv2.FILLED)
            self.manager.delete_contour(self.selected_contour_idx, self.input_image_path)
            self.overlay_image = cv2.addWeighted(self.input_image_rgb, 1 - self.alpha, self.mask_colored, self.alpha, 0)
            self.display_image = self.overlay_image.copy()
            self.update_image(self.display_image)

    def update_image(self, image):
        image_pil = Image.fromarray(image)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_tk = image_tk
        self.create_image(0, 0, anchor=tk.NW, image=image_tk)

def main():
    outdir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(outdir, exist_ok=True)
    input_path = 'niwatori.jpg'
    output_path = os.path.join(outdir, 'niwatori-remove.png')
    class_id = 1

    processor = ImageProcessor()
    if processor.remove_background(input_path, output_path):
        mask = processor.apply_mask_to_background(output_path)
        if mask is not None:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            manager = AnnotationManager(outdir, class_id)
            manager.save_contours_and_labels(mask, contours, input_path)

            root = tk.Tk()
            tool = Deleter(root, input_path, mask, contours, outdir, class_id)
            root.mainloop()

if __name__ == "__main__":
    main()
