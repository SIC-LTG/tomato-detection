import cv2
import numpy as np

def prepare_image(img):
    resized = cv2.resize(img, (224, 224))
    return np.expand_dims(resized / 255.0, axis=0)
