import requests
import numpy as np
import cv2

#Ambil gambar melalui URL/WEBSERVER
def get_image(url):
    res = requests.get(url)
    img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)
    return img

img = get_image("http://192.168.1.101/capture")
cv2.imshow("Tomat", img)
cv2.waitKey(0)

#Ambil gambar melalui LAPTOP CAMERA (TESTING)
def get_image_from_webcam():
    cap = cv2.VideoCapture(0)  # 0 biasanya default webcam
    ret, frame = cap.read()
    cap.release()
    if ret:
        return frame
    else:
        raise Exception("Gagal membuka kamera.")
