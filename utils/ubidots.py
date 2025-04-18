import requests

UBIDOTS_TOKEN = "BBUS-mMrdCjC7r3OzP5T4AhsZOK9CDmwu2Y"
DEVICE_LABEL = "esp32cam-detector"

def send_to_ubidots(variable_label, value):
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/esp32cam-detector"
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {variable_label: value}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()