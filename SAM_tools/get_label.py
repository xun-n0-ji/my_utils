import os
import cv2

def load_data(image_path, label_dir, masks_dir, class_id):
    data = {
        "mask": [],
        "label": []
    }
    
    # Load labels from .txt file
    label_file = os.path.join(label_dir, f"{image_path}.txt")
    if os.path.exists(label_file):
        with open(label_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data["label"].append(line.strip())
    else:
        print(f"Label file {label_file} not found.")

    # Load mask images
    idx = 0
    while True:
        mask_file = os.path.join(masks_dir, f"{image_path}_classID{class_id}_{idx}.png")
        if os.path.exists(mask_file):
            mask = cv2.imread(mask_file, cv2.IMREAD_UNCHANGED)
            if mask is not None:
                data["mask"].append(mask)
            else:
                print(f"Failed to read mask file {mask_file}.")
        else:
            break
        idx += 1

    return data

# Example usage
image_path = "example_image"
label_dir = "/path/to/labels"
masks_dir = "/path/to/masks"
class_id = 1

data = load_data(image_path, label_dir, masks_dir, class_id)
print(data)
