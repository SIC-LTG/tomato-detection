import streamlit as st
import cv2
import time
import requests
import numpy as np
from datetime import datetime
from utils.tomato_detector_v2 import predict_frame, save_to_csv, detect_tomato_area
from utils.ubidots import send_to_ubidots  # ✅ Tambahan ini

# Fungsi ambil frame dari ESP32-CAM
def get_frame_from_esp32(camera_url):
    try:
        response = requests.get(camera_url, timeout=1)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Gagal ambil frame: {e}")
        return None

# Streamlit app
def run_streamlit_app(camera_url='http://192.168.1.7/capture', use_roi=True):
    st.title("Tomato Freshness Detector -")

    st.sidebar.header("SIC-LUTUNG SOPAN")
    st.sidebar.subheader("1. Rafi Putra Fauzi")
    st.sidebar.subheader("2. Zidane Akmal")
    st.sidebar.subheader("3. Rutji Edra Kedoh")
    st.sidebar.subheader("4. Davicho Widyatmoko")

    image_placeholder = st.empty()
    status_placeholder = st.empty()
    prediction_placeholder = st.empty()
    probability_placeholder = st.empty()

    fps_limit = 15  # Max 15 frames per second
    prev_time = 0

    try:
        while True:
            # Batas FPS
            current_time = time.time()
            if current_time - prev_time < 1.0 / fps_limit:
                continue
            prev_time = current_time

            frame = get_frame_from_esp32(camera_url)
            if frame is None:
                status_placeholder.error("❌ Gagal ambil gambar dari ESP32-CAM")
                continue

            # Prediksi dan deteksi
            label, color, prob, cx, cy, cs = predict_frame(frame, use_roi=use_roi)
            tomato_boxes = detect_tomato_area(frame)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Kirim ke Ubidots
            status_label = "busuk" if label == "Tomat Sudah Membusuk" else "segar"
            success, result = send_to_ubidots("tomato_status", status_label)
            if success:
                print("✅ Data terkirim ke Ubidots:", result)
            else:
                print("❌ Gagal kirim ke Ubidots:", result)

            for (x, y, w, h) in tomato_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                if label == "Tomat Sudah Membusuk":
                    cv2.putText(frame, "Busuk!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Update tampilan
            image_placeholder.image(frame, caption=f"{label} ({prob:.2f})", channels="BGR", use_container_width=True)
            save_to_csv(timestamp, label, prob)

            status_placeholder.write(f"🕒 {timestamp}")
            prediction_placeholder.write(f"🧠 Prediction: {label}")
            probability_placeholder.write(f"📊 Probability: {prob:.2f}")

    except Exception as e:
        st.error(f"⚠ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    run_streamlit_app(camera_url='http://192.168.1.7/capture')
