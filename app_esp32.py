import streamlit as st
from datetime import datetime
import time
from utils.tomato_detector_esp32 import get_image_from_esp32, predict_frame, save_to_csv

# Fungsi Streamlit untuk menampilkan UI
def run_streamlit_app(esp32_url="http://192.168.1.30/capture", roi_size=0.6, use_roi=True):
    st.title("Tomato Freshness Detector - ESP32 Camera")

    st.sidebar.header("SIC-LUTUNG SOPAN")
    st.sidebar.subheader("1. Rafi Putra Fauzi")
    st.sidebar.subheader("2. Zidane Akmal")
    st.sidebar.subheader("3. Rutji Edra Kedoh")
    st.sidebar.subheader("4. Davicho Widyatmoko")
    
    # Add ROI controls to sidebar
    use_roi = st.sidebar.checkbox("Use detection frame", value=True)
    roi_size = st.sidebar.slider("Frame size", min_value=0.3, max_value=0.9, value=0.6, step=0.1)
    
    # ESP32 camera settings
    esp32_url = st.sidebar.text_input("ESP32-CAM URL", value="http://192.168.1.30/capture")
    
    # Add a refresh rate control
    refresh_rate = st.sidebar.slider("Refresh rate (seconds)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)

    # Tempat untuk menampilkan gambar secara dinamis
    image_placeholder = st.empty()
    
    # Status indicators
    status_placeholder = st.empty()
    prediction_placeholder = st.empty()
    probability_placeholder = st.empty()
    
    # Connection status
    connection_status = st.sidebar.empty()

    try:
        while True:
            # Mengambil gambar dari ESP32-CAM
            connection_status.info("Connecting to ESP32-CAM...")
            frame = get_image_from_esp32(esp32_url)
            
            if frame is None:
                connection_status.error("Failed to connect to ESP32-CAM. Check the URL and connection.")
                time.sleep(2)  # Wait before retrying
                continue
            else:
                connection_status.success("Connected to ESP32-CAM")

            # Prediksi dan simpan log
            label, color, prob, display_frame = predict_frame(frame, use_roi=use_roi, roi_size=roi_size)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Menampilkan gambar secara dinamis (streaming)
            image_placeholder.image(display_frame, caption=f"{label} ({prob:.2f})", channels="BGR", use_container_width=True)

            # Menyimpan hasil prediksi ke CSV
            save_to_csv(timestamp, label, prob)

            # Update status
            status_placeholder.write(f"Timestamp: {timestamp}")
            prediction_placeholder.write(f"Prediction: {label}")
            probability_placeholder.write(f"Probability: {prob:.2f}")
            
            # Add a delay based on the refresh rate
            time.sleep(refresh_rate)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    run_streamlit_app()
