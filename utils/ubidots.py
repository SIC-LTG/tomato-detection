import requests

def send_result_to_ubidots(token, label, value):
    url = "https://industrial.api.ubidots.com/api/v1.6/devices/tomat-detector"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    data = {label: value}
    return requests.post(url, headers=headers, json=data)
