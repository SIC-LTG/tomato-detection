import cv2
import numpy as np
import csv
from datetime import datetime
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
import requests

# MENGGUNAKAN ESP32 CAM

# Load model
model = load_model(r'model\tomato_fresh_detector(Jupiter)V2.h5')
target_size = (150, 150)

# CSV log
log_filename = r'model\TomatoFreshDetector_Hystory.csv'
with open(log_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Prediction', 'Probability'])

# Fungsi untuk mengambil gambar dari stream ESP32-CAM
def get_frame_from_stream(url):
    """Ambil gambar dari stream ESP32-CAM dalam bentuk frame"""
    try:
        img_resp = requests.get(url, stream=True)
        if img_resp.status_code == 200:
            img_array = np.asarray(bytearray(img_resp.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return frame
    except Exception as e:
        print(f"Error getting frame from stream: {e}")
    return None

def detect_tomato_area(frame):
    """Deteksi area tomat pakai HSV color range sederhana"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Range warna merah-oranye untuk tomat
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tomato_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # threshold area minimal
            x, y, w, h = cv2.boundingRect(cnt)
            tomato_boxes.append((x, y, w, h))
    return tomato_boxes

def predict_frame(frame, use_roi=True):
    h, w, _ = frame.shape
    if use_roi:
        crop_size = min(h, w) // 2
        center_x, center_y = w // 2, h // 2

        cropped = frame[
            center_y - crop_size // 2: center_y + crop_size // 2,
            center_x - crop_size // 2: center_x + crop_size // 2
        ]
    else:
        cropped = frame  # Gunakan frame penuh jika ROI tidak aktif

    img = cv2.resize(cropped, target_size)
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    prob = prediction[0][0]

    if prob < 0.10:
        label = 'Gambar Kurang Jelas'
        color = (255, 255, 0)
    elif 0.10 <= prob < 0.940000:
        label = 'Tomat Masih Segar'
        color = (0, 255, 0)
    else:
        label = 'Tomat Sudah Membusuk'
        color = (0, 0, 255)

    return label, color, prob, center_x, center_y, crop_size

def save_to_csv(timestamp, label, prob):
    with open(log_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, label, f"{prob:.4f}"])



# MENGGUNAKAN WEBCAM LAPTOP

# # Load model
# model = load_model(r'model\tomato_fresh_detector(Jupiter)V2.h5')
# target_size = (150, 150)

# # CSV log
# log_filename = r'model\TomatoFreshDetector_Hystory.csv'
# with open(log_filename, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Timestamp', 'Prediction', 'Probability'])

# def detect_tomato_area(frame):
#     """Deteksi area tomat pakai HSV color range sederhana"""
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     # Range warna merah-oranye untuk tomat
#     lower_red = np.array([0, 100, 100])
#     upper_red = np.array([10, 255, 255])
#     mask1 = cv2.inRange(hsv, lower_red, upper_red)

#     lower_red2 = np.array([160, 100, 100])
#     upper_red2 = np.array([179, 255, 255])
#     mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

#     mask = mask1 + mask2

#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     tomato_boxes = []
#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if area > 500:  # threshold area minimal
#             x, y, w, h = cv2.boundingRect(cnt)
#             tomato_boxes.append((x, y, w, h))
#     return tomato_boxes

# def predict_frame(frame, use_roi=True, roi_size=0.6):
#     h, w, _ = frame.shape
#     crop_size = min(h, w) // 2
#     center_x, center_y = w // 2, h // 2

#     if use_roi:
#         cropped = frame[
#             center_y - crop_size // 2: center_y + crop_size // 2,
#             center_x - crop_size // 2: center_x + crop_size // 2
#         ]
#     else:
#         cropped = frame

#     img = cv2.resize(cropped, target_size)
#     img_array = img_to_array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)
#     prediction = model.predict(img_array)
#     prob = prediction[0][0]

#     if prob < 0.10:
#         label = 'Gambar Kurang Jelas'
#         color = (255, 255, 0)
#     elif 0.10 <= prob < 0.940000:
#         label = 'Tomat Masih Segar'
#         color = (0, 255, 0)
#     else:
#         label = 'Tomat Sudah Membusuk'
#         color = (0, 0, 255)

#     return label, color, prob, center_x, center_y, crop_size

# def save_to_csv(timestamp, label, prob):
#     """Simpan hasil prediksi ke CSV"""
#     with open(log_filename, mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([timestamp, label, f"{prob:.4f}"])
