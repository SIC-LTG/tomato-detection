import requests
import numpy as np
import cv2

def get_image(url):
    res = requests.get(url)
    img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)
    return img

img = get_image("http://192.168.1.101/capture")
cv2.imshow("Tomat", img)
cv2.waitKey(0)
