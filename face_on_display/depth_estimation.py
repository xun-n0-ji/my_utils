import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
try:
    # linux
    import tflite_runtime.interpreter as tflite
except ImportError:
    # win
    from tensorflow import lite as tflite

class DepthEstimation:
    def __init__(self):
        self.load_model()

    def load_model(self, model = None):
        if model is None:
            model_dir_path = fr"{os.path.abspath(os.path.dirname(os.path.abspath(__file__)))}/model"
            self.interpreter = tflite.Interpreter(fr"{model_dir_path}/lite-model_midas_v2_1_small_1_lite_1.tflite")
            self.interpreter.allocate_tensors()
        else:
            self.interpreter = tflite.Interpreter(model)
            self.interpreter.allocate_tensors()

    def preprocess(self, image_cv2):
        input_details = self.interpreter.get_input_details()
        input_shape = input_details[0]['shape']
        inputHeight, inputWidth, channels, = input_shape[1], input_shape[2], input_shape[3]

        output_details = self.interpreter.get_output_details()
        output_shape = output_details[0]['shape']
        outputHeight, outputWidth = output_shape[1], output_shape[2]

        # Input values should be from -1 to 1 with a size of 128 x 128 pixels for the fornt model
        # and 256 x 256 pixels for the back model
        image_resized = cv2.resize(image_cv2, (inputWidth,inputHeight),interpolation = cv2.INTER_CUBIC).astype(np.float32)

        # Scale input pixel values to -1 to 1
        mean=[0.485, 0.456, 0.406]
        std=[0.229, 0.224, 0.225]
        image_resized = ((image_resized/ 255.0 - mean) / std).astype(np.float32)
        image_resized = image_resized[np.newaxis,:,:,:]
        return image_resized, input_details, output_details, outputHeight, outputWidth

    def get_estimate_depth(self, image):
        preprocessed_image, input_details, output_details, outputHeight, outputWidth = self.preprocess(image)
        # Peform inference
        self.interpreter.set_tensor(input_details[0]['index'], preprocessed_image)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(output_details[0]['index'])
        output = output.reshape(outputHeight, outputWidth)

        # Normalize estimated depth to have values between 0 and 255
        depth_min = output.min()
        depth_max = output.max()
        normalizedDisparity = (255 * (output - depth_min) / (depth_max - depth_min)).astype("uint8")

        # Resize disparity map to the sam size as the image inference
        estimatedDepth = cv2.resize(normalizedDisparity, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_CUBIC)
        colorDepth = cv2.applyColorMap(estimatedDepth, cv2.COLORMAP_MAGMA)
        #np.savetxt("test.csv", estimatedDepth, delimiter=",", fmt="%d")
        return estimatedDepth, colorDepth
    
    def get_estimate_depth_mask(self, image, threshold):
        estimated_depth, _ = self.get_estimate_depth(image)
        depth_estimated_mask = (estimated_depth > threshold)
        return depth_estimated_mask

        