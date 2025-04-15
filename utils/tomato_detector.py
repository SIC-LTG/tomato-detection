import cv2
import numpy as np
import csv
import time
from datetime import datetime
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
import requests

# ==============================================================
# MENGGUNAKAN CAMERA LAPTOP

# # Load model
# model = load_model(r'.\model\tomato_fresh_detector(Jupiter)V2.h5')
# target_size = (150, 150)

# #Buat file CSV log
# log_filename = r'.\model\TomatoFreshDetector_Hystory.csv'
# with open(log_filename, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Timestamp', 'Prediction', 'Probability'])

# def predict_frame(frame):
#     img = cv2.resize(frame, target_size)
#     img_array = img_to_array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)
#     prediction = model.predict(img_array)
#     prob = prediction[0][0]

#     if prob < 0.10:
#         label = 'Gambar Kurang Jelas'
#         color = (255, 255, 0)
#     elif 0.10 <= prob < 0.970000:
#         label = 'Tomat Masih Segar'
#         color = (0, 255, 0)
#     else:
#         label = 'Tomat Sudah Membusuk'
#         color = (0, 0, 255)

#     return label, color, prob

# def run_webcam_with_logging():
#     cap = cv2.VideoCapture(0)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         label, color, prob = predict_frame(frame)
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # Simpan log ke CSV
#         with open(log_filename, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([timestamp, label, f"{prob:.4f}"])


#         # Tampilkan prediksi di layar
#         cv2.putText(frame, f'{label} ({prob:.2f})', (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
#         cv2.imshow('Tomato Freshness Detector (Webcam + Logging)', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     print(f"📁 Log prediksi disimpan di: {log_filename}")

# # Jalankan!
# run_webcam_with_logging()

# ------------------------------------------------------------------------------

# MENGGUNAKAN ESP32 CAM


# Load model
model = load_model(r'model\tomato_fresh_detector(Jupiter)V2.h5')
target_size = (150, 150)

# Fungsi untuk mengambil gambar dari ESP32-CAM
def get_image_from_esp32(url):
    res = requests.get(url)  # Mengambil gambar dari ESP32 Web Server
    img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)  # Decode gambar menjadi array OpenCV
    return img

# Fungsi prediksi
def predict_frame(frame):
    img = cv2.resize(frame, target_size)
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    prob = prediction[0][0]

    if prob < 0.10:
        label = 'Gambar Kurang Jelas'
        color = (255, 255, 0)
    elif 0.10 <= prob < 0.970000:
        label = 'Tomat Masih Segar'
        color = (0, 255, 0)
    else:
        label = 'Tomat Sudah Membusuk'
        color = (0, 0, 255)

    return label, color, prob

# Fungsi untuk menyimpan hasil prediksi ke CSV
def save_to_csv(timestamp, label, prob, file_path='./model/TomatoFreshDetector_Hystory.csv'):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, label, f"{prob:.4f}"])
