import time
import json
import board
import wifi
import socketpool
import usb_hid
import adafruit_requests
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

# Create and set up a TCP socket server
server_socket = socketpool.SocketPool(wifi.radio)
server = server_socket.socket(socketpool.AF_INET, socketpool.SOCK_STREAM)
server.bind(('0.0.0.0', 5000))  # Bind to all available interfaces on port 5000
server.listen(1)  # Start listening for connections

print("Server running on IP: {0}, Port 5000... Waiting for connections.".format(ip_address))

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

while True:
    try:
        print("Waiting for a client to connect...")
        conn, addr = server.accept()
        print(f"Connection from {addr}")

        while True:  # Keep the connection open
            try:
                # Receive JSON data from the client
                request_data = conn.recv(1024)  # Read 1024 bytes at a time
                if request_data:
                    try:
                        data = json.loads(request_data)
                        print(f"Received JSON: {data}")

                        # Handle key, string, and special combo based on the payload
                        if "key" in data:
                            response = send_key(data["key"])
                        elif "string" in data:
                            response = send_string(data["string"])
                        elif "special" in data:
                            response = send_special_combo(data["special"])
                        else:
                            response = "Invalid request"

                    except json.JSONDecodeError:
                        response = "Invalid JSON"
                    except Exception as e:
                        response = f"Error: {str(e)}"

                    # Send the response back to the client
                    conn.sendall(response.encode('utf-8'))

                else:
                    print("No data received, closing connection...")
                    break  # No data received, close connection

            except Exception as e:
                print(f"Error during communication: {str(e)}")
                break  # Exit inner loop on error

        # Close the connection after handling the communication loop
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")
        time.sleep(1)  # Sleep before trying again
