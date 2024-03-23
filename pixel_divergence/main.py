import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from imager import Imager

class ArrayImageViewer():
    def __init__(self, root, N, M):
        self.__main = root
        self.__main.title("Array Image Viewer")
        self.image_width = N
        self.image_height = M
        self.screen_width = self.__main.winfo_screenwidth()
        self.screen_height = self.__main.winfo_screenheight()
        self.window_width = self.screen_width // 2
        self.window_height = self.screen_height // 2
        self.__main.geometry(f"{self.window_width}x{self.window_height}+{self.window_width//2}+{self.window_height//2}")
        
        #self.array = np.random.randint(0, 256, (N, M, 3), dtype=np.uint8)
        self.array = np.zeros((N, M, 3), dtype=np.uint8)
        self.canvas = tk.Canvas(self.__main)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.width = self.canvas.winfo_reqwidth()
        self.height = self.canvas.winfo_reqheight()
        self.canvas.config(width=int(self.width*0.9), height=int(self.height*0.9))
        self.show_image()
        
        self.__main.bind("<Configure>", self.on_resize)
        self.__main.mainloop()

    def show_image(self):
        self.array = Imager.image_processing_3ch(self.array)
        image = Image.fromarray(self.array)
        new_width, new_height = self.adjust_image_size(self.image_height, self.image_width, int(self.height*0.9), int(self.width*0.9))
        image = image.resize((new_width, new_height), Image.NEAREST)
        #image.thumbnail((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(self.width/2, self.height/2, image=photo)
        self.canvas.image = photo  # to prevent garbage collection
        self.canvas.after(200, self.show_image)

    @staticmethod
    def adjust_image_size(height, width, ref_height, ref_width):
        # ウィンドウサイズに合わせて画像を拡大表示
        if ref_width / ref_height < width / height:
            # ウィンドウの幅に合わせて拡大
            new_width = ref_width
            new_height = int(ref_width * height / width)
        else:
            # ウィンドウの高さに合わせて拡大
            new_height = ref_height
            new_width = int(ref_height * width / height)

        return new_height, new_width

    def on_resize(self, event):
        self.canvas.delete("all")
        self.width = event.width
        self.height = event.height
        self.canvas.config(width=int(self.width*0.9), height=int(self.height*0.9))
        self.show_image()

if __name__ == "__main__":
    N = 50
    M = 50
    root = tk.Tk()
    app = ArrayImageViewer(root, N, M)
