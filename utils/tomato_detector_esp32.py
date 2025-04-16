import cv2
import numpy as np
import csv
import time
from datetime import datetime
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
import requests

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
model = load_model(r'model\tomato_fresh_detector(Jupiter)V2.h5')
target_size = (150, 150)

# Fungsi untuk mengambil gambar dari ESP32-CAM
def get_image_from_esp32(url):
    """
    Get an image from ESP32-CAM
    
    Args:
        url: URL of the ESP32-CAM capture endpoint
        
    Returns:
        The captured frame or None if capture failed
    """
    try:
        res = requests.get(url, timeout=5)  # Mengambil gambar dari ESP32 Web Server
        if res.status_code == 200:
            img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)  # Decode gambar menjadi array OpenCV
            return img
        else:
            print(f"Error: ESP32-CAM returned status code {res.status_code}")
            return None
    except Exception as e:
        print(f"Error connecting to ESP32-CAM: {e}")
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
def save_to_csv(timestamp, label, prob, file_path='./model/TomatoFreshDetector_Hystory.csv'):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, label, f"{prob:.4f}"])
