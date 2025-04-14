# Tomat Detektor (ESP32-CAM + AI + Ubidots)

Project ini mendeteksi apakah tomat dalam gambar segar atau busuk menggunakan ESP32-CAM dan model AI. Hasil klasifikasi dikirim ke Ubidots dan ditampilkan dalam dashboard Streamlit.

## Struktur
- `model/` : berisi model AI (format .h5)
- `utils/` : preprocessing dan pengiriman data
- `esp32_test/` : tes pengambilan gambar
- `app.py` : dashboard utama
