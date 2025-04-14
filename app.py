import streamlit as st
from keras.models import load_model
from utils.preprocess import prepare_image
from utils.ubidots import send_result_to_ubidots
import requests
import cv2
import numpy as np

model = load_model("model/model_tomat.h5")
UBIDOTS_TOKEN = "xxxxx"
ESP32_URL = "http://192.168.1.101/capture"

def get_image():
    res = requests.get(ESP32_URL)
    img = cv2.imdecode(np.frombuffer(res.content, np.uint8), -1)
    return img

st.title("Deteksi Tomat Fresh atau Busuk")
if st.button("Ambil Gambar & Deteksi"):
    img = get_image()
    st.image(img, caption="Gambar dari ESP32-CAM", channels="BGR")
    pred = model.predict(prepare_image(img))[0]
    label = "Fresh" if pred[0] > 0.5 else "Busuk"
    st.success(f"Hasil Deteksi: {label}")
    send_result_to_ubidots(UBIDOTS_TOKEN, "deteksi", 1 if label == "Fresh" else 0)
