import cv2
import numpy as np
import csv
from datetime import datetime
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore

# Load model
model = load_model(r'C:\Users\Zidane Akmal\Downloads\Clone Machine\tomato-detection\model\tomato_fresh_detector(Jupiter)V2.h5')
target_size = (150, 150)

# CSV log
log_filename = r'C:\Users\Zidane Akmal\Downloads\Clone Machine\tomato-detection\model\TomatoFreshDetector_Hystory.csv'
with open(log_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Prediction', 'Probability'])

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

def predict_frame(frame):
    h, w, _ = frame.shape
    crop_size = min(h, w) // 2
    center_x, center_y = w // 2, h // 2

    cropped = frame[
        center_y - crop_size // 2: center_y + crop_size // 2,
        center_x - crop_size // 2: center_x + crop_size // 2
    ]

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

def run_webcam_with_logging():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        label, color, prob, cx, cy, cs = predict_frame(frame)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, label, f"{prob:.4f}"])

        # Deteksi area tomat untuk tracking visual
        tomato_boxes = detect_tomato_area(frame)
        for (x, y, w, h) in tomato_boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            if label == "Tomat Sudah Membusuk":
                cv2.putText(frame, "Busuk!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        

        cv2.putText(frame, f'{label} ({prob:.2f})', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.imshow('Tomato Detector + Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"📁 Log prediksi disimpan di: {log_filename}")

# Jalankan program
run_webcam_with_logging()

# ------------------------------------------------------------------------------

# MENGGUNAKAN ESP32 CAM


# Load model
# model = load_model(r'model\tomato_fresh_detector(Jupiter)V2.h5')
# target_size = (150, 150)

# # Fungsi untuk mengambil gambar dari ESP32-CAM
# def get_image_from_esp32(url):
#     res = requests.get(url)  # Mengambil gambar dari ESP32 Web Server
#     img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)  # Decode gambar menjadi array OpenCV
#     return img

# # Fungsi prediksi
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

# # Fungsi untuk menyimpan hasil prediksi ke CSV
# def save_to_csv(timestamp, label, prob, file_path='./model/TomatoFreshDetector_Hystory.csv'):
#     with open(file_path, mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([timestamp, label, f"{prob:.4f}"])
