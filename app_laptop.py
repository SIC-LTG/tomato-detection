import streamlit as st
from datetime import datetime
import cv2
import time
from utils.tomato_detector_laptop import predict_frame, save_to_csv

# Fungsi Streamlit untuk menampilkan UI
def run_streamlit_app(camera_index=0, roi_size=0.6, use_roi=True):
    st.title("Tomato Freshness Detector - Laptop Camera")

    st.sidebar.header("SIC-LUTUNG SOPAN")
    st.sidebar.subheader("1. Rafi Putra Fauzi")
    st.sidebar.subheader("2. Zidane Akmal")
    st.sidebar.subheader("3. Rutji Edra Kedoh")
    st.sidebar.subheader("4. Davicho Widyatmoko")
    
    # Add ROI controls to sidebar
    use_roi = True
    roi_size = st.sidebar.slider("Frame size", min_value=0.3, max_value=0.9, value=0.6, step=0.1)
    
    # # Camera settings
    # camera_index = st.sidebar.number_input("Camera Index", min_value=0, max_value=10, value=0, step=1)

    # Tempat untuk menampilkan gambar secara dinamis
    image_placeholder = st.empty()
    
    # Status indicators
    status_placeholder = st.empty()
    prediction_placeholder = st.empty()
    probability_placeholder = st.empty()
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_index)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        st.error(f"Error: Could not open camera {camera_index}")
        return

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            if not ret:
                status_placeholder.error("Error: Failed to capture image")
                time.sleep(1)
                continue
                
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
            
            # Add a small delay to reduce CPU usage
            time.sleep(0.1)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Release the camera when the app is stopped
        cap.release()

if __name__ == "__main__":
    run_streamlit_app()
