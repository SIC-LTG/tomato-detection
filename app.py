import streamlit as st
from datetime import datetime
from utils.tomato_detector import get_image_from_esp32, predict_frame, save_to_csv  # Mengimpor fungsi dari utils/functions.py

# Fungsi Streamlit untuk menampilkan UI
def run_streamlit_app(esp32_url="http://192.168.1.30/capture"):
    st.title("Tomato Freshness Detector")

    st.sidebar.header("SIC-LUTUNG SOPAN")
    st.sidebar.subheader("1. Rafi Putra Fauzi")
    st.sidebar.subheader("2. Zidane Akmal")
    st.sidebar.subheader("3. Rutji Edra Kedoh")
    st.sidebar.subheader("4. Davicho Widyatmoko")

    # Tempat untuk menampilkan gambar secara dinamis
    image_placeholder = st.empty()

    while True:
        # Mengambil gambar dari ESP32-CAM
        frame = get_image_from_esp32(esp32_url)
        if frame is None:
            st.error("Gambar tidak tersedia, pastikan ESP32-CAM terhubung dengan benar.")
            break

        # Prediksi dan simpan log
        label, color, prob = predict_frame(frame)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Menampilkan gambar secara dinamis (streaming)
        image_placeholder.image(frame, caption=f"{label} ({prob:.2f})", channels="BGR", use_container_width=True)

        # Menyimpan hasil prediksi ke CSV
        save_to_csv(timestamp, label, prob)

        st.write(f"Timestamp: {timestamp}")
        st.write(f"Prediction: {label}")
        st.write(f"Probability: {prob:.2f}")

if __name__ == "__main__":
    run_streamlit_app(esp32_url="http://192.168.1.30/capture")
