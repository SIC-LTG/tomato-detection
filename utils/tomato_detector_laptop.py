import cv2
import numpy as np
import csv
import time
from datetime import datetime
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore

# Function to draw a detection frame on the image
def draw_detection_frame(frame, roi_size=0.6):
    """
    Draw a detection frame in the middle of the image
    
    Args:
        frame: The input image
        roi_size: Size of the ROI as a fraction of the image size (0.0-1.0)
        
    Returns:
        frame: The image with the detection frame drawn
        (x, y, w, h): Coordinates of the ROI
    """
    height, width = frame.shape[:2]
    
    # Calculate ROI dimensions
    roi_width = int(width * roi_size)
    roi_height = int(height * roi_size)
    
    # Calculate ROI position (centered)
    x = (width - roi_width) // 2
    y = (height - roi_height) // 2
    
    # Draw the rectangle
    cv2.rectangle(frame, (x, y), (x + roi_width, y + roi_height), (0, 255, 0), 2)
    
    # Add text above the rectangle
    cv2.putText(frame, "Place tomato here", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame, (x, y, roi_width, roi_height)

# Function to extract the region of interest
def extract_roi(frame, roi_coords):
    """
    Extract the region of interest from the frame
    
    Args:
        frame: The input image
        roi_coords: (x, y, w, h) coordinates of the ROI
        
    Returns:
        The cropped image containing only the ROI
    """
    x, y, w, h = roi_coords
    return frame[y:y+h, x:x+w]

# Load model
model = load_model(r'.\model\tomato_fresh_detector(Jupiter)V2.h5')
target_size = (150, 150)

# Function to get frame from laptop camera
def get_frame_from_laptop(camera_index=0):
    """
    Capture a frame from the laptop camera
    
    Args:
        camera_index: Index of the camera (default 0)
        
    Returns:
        The captured frame or None if capture failed
    """
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        return frame
    else:
        return None

# Fungsi prediksi
def predict_frame(frame, use_roi=True, roi_size=0.6):
    # Draw detection frame and get ROI coordinates
    display_frame, roi_coords = draw_detection_frame(frame, roi_size)
    
    # If use_roi is True, only process the region of interest
    if use_roi:
        # Extract the region of interest
        roi = extract_roi(frame, roi_coords)
        
        # Process the ROI
        img = cv2.resize(roi, target_size)
    else:
        # Process the entire frame
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

    return label, color, prob, display_frame

# Fungsi untuk menyimpan hasil prediksi ke CSV
def save_to_csv(timestamp, label, prob, file_path=r'.\model\TomatoFreshDetector_Hystory.csv'):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, label, f"{prob:.4f}"])

# Function to run webcam continuously (for testing outside of Streamlit)
def run_webcam_with_logging(use_roi=True, roi_size=0.6):
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        label, color, prob, display_frame = predict_frame(frame, use_roi=use_roi, roi_size=roi_size)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simpan log ke CSV
        save_to_csv(timestamp, label, prob)

        # Tampilkan prediksi di layar
        cv2.putText(display_frame, f'{label} ({prob:.2f})', (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.imshow('Tomato Freshness Detector (Webcam + Logging)', display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"📁 Log prediksi disimpan di: ./model/TomatoFreshDetector_Hystory.csv")

# For direct testing
if __name__ == "__main__":
    run_webcam_with_logging()
