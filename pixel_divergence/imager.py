import cv2
import numpy as np
import time

class Imager:
    """kernel = np.array([[0, 0, 1/64, 0, 0],
                                [0, 1/64, 3/64, 1/64, 0],
                                [1/64, 3/64, 7/16, 3/64, 1/64],
                                [0, 1/64, 3/64, 1/64, 0],
                                [0, 0, 1/64, 0, 0]])"""
    kernel = np.array([[2/32, 3/32, 2/32],
                        [3/32, 6/16, 3/32],
                        [2/32, 3/32, 2/32]])
    def __init__(self):
        pass

    @classmethod
    def image_processing_3ch(cls, image):
        image = cls.generate_anomaly_3ch(image, size = 4)
        image = cls.convolution_3ch(image, cls.kernel)
        return image
        
    @staticmethod
    def convolution(image, kernel):
        # 入力画像のサイズとカーネルのサイズを取得
        image_height, image_width = image.shape[0:2]
        kernel_height, kernel_width = kernel.shape[0:2]

        # 畳み込み後の画像を初期化
        convolved_image = np.zeros_like(image)

        # カーネルの中心位置
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2

        # ゼロパディング
        padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='constant')

        # 畳み込み演算
        for i in range(image_height):
            for j in range(image_width):
                convolved_image[i, j] = np.sum(padded_image[i:i+kernel_height, j:j+kernel_width] * kernel)

        return convolved_image
    
    @staticmethod
    def convolution_3ch(image, kernel):
        
        start = time.perf_counter()
        # 入力画像のサイズとカーネルのサイズを取得
        image_height, image_width, image_channels = image.shape
        kernel_height, kernel_width = kernel.shape[0:2]

        # 畳み込み後の画像を初期化
        convolved_image = np.zeros_like(image)

        # カーネルの中心位置
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2

        # ゼロパディング
        padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width), (0, 0)), mode='constant')

        # 畳み込み演算
        for i in range(image_height):
            for j in range(image_width):
                for c in range(image_channels):
                    convolved_image[i, j, c] = np.sum(padded_image[i:i+kernel_height, j:j+kernel_width, c] * kernel)
        #print(time.perf_counter() - start)
        return convolved_image
    
    @staticmethod
    def generate_anomaly(image, size = 2):
        image_height, image_width = image.shape[0:2]
        
        pixel_num = (image_height - size)*(image_width - size)
        pixel = np.random.randint(0, pixel_num)
        pixel_y, pixel_x = pixel//(image_width - size), pixel%(image_height - size)
        #possibility = np.random.default_rng().poisson(lam=1)
        possibility = np.random.default_rng().random(1)
        if possibility < 0.05:
            image[pixel_y:pixel_y+size, pixel_x:pixel_x+size] = 255
        return image
    
    @staticmethod
    def generate_anomaly_3ch(image, size = 2):
        image_height, image_width = image.shape[0:2]
        
        pixel_num = (image_height - size)*(image_width - size)
        pixel = np.random.randint(0, pixel_num)
        pixel_y, pixel_x = pixel//(image_width - size), pixel%(image_height - size)
        #possibility = np.random.default_rng().poisson(lam=1)
        possibility = np.random.default_rng().random(1)
        if possibility < 0.05:
            image[pixel_y:pixel_y+size, pixel_x:pixel_x+size] = [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)]
        return image

if __name__ == "__main__":
    array = np.zeros((5, 5))
    result = Imager.generate_anomaly(array)
    print(result)