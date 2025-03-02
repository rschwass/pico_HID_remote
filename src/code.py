import time
import json
import board
import wifi
import socketpool
import usb_hid
import adafruit_requests
from adafruit_httpserver import Server, Request, Response, GET
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

import config  # Import the config.py file

print("Starting...")

# Wi-Fi Credentials
SSID = config.SSID
PASSWORD = config.PASSWORD
SERVER_BASE_URL = config.API_URL

# Connect to Wi-Fi
print(f"Connecting to {SSID}...")
try:
    wifi.radio.connect(SSID, PASSWORD)
    ip_address = wifi.radio.ipv4_address
    print(f"Connected! IP Address: {ip_address}")
except Exception as e:
    print(f"Wi-Fi Error: {e}")
    time.sleep(10)
    exit()

# Send GET request with IP as a parameter
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

try:
    url = f"{SERVER_BASE_URL}?ip={ip_address}"
    response = requests.get(url)
    print(f"Server Response: {response.text}")
except Exception as e:
    print(f"Failed to send request: {e}")

# Start HID Keyboard
kbd = Keyboard(usb_hid.devices)

# Special Key Combos
SPECIAL_KEYS = {
    "CTRL_ALT_DEL": [Keycode.CONTROL, Keycode.ALT, Keycode.DELETE],
    "ALT_F4": [Keycode.ALT, Keycode.F4],
    "CTRL_C": [Keycode.CONTROL, Keycode.C],
}

# Start HTTP Server
#server = pool.socket()
server = Server(pool, "/static", debug=True)

def send_key(key_name):
    key = getattr(Keycode, key_name.upper(), None)
    if key:
        kbd.send(key)
        return f"Sent key: {key_name}"
    return "Invalid key"

def send_string(text):
    for char in text:
        if char.upper() in Keycode.__dict__:
            kbd.send(getattr(Keycode, char.upper()))
        time.sleep(0.1)  # Small delay
    return f"Sent string: {text}"

def send_special_combo(combo_name):
    combo = SPECIAL_KEYS.get(combo_name.upper())
    if combo:
        kbd.press(*combo)
        time.sleep(0.1)
        kbd.release_all()
        return f"Sent special combo: {combo_name}"
    return "Invalid special combo"

print("Server running... Listening for requests.")

@server.route("/", GET)
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"ok", content_type='text/html')




server.serve_forever(str(wifi.radio.ipv4_address))