import time
import json
import wifi # type: ignore
import socketpool
import ssl
import config  # Wi-Fi & Server Config
from hid_controller import send_key, send_string, send_special_combo  # Import HID functions

print("Starting...")

# Wi-Fi Credentials
SSID = config.SSID
PASSWORD = config.PASSWORD
SERVER_HOST = config.SERVER_HOST  # Your server's IP or hostname
SERVER_PORT = config.SERVER_PORT  # The SSL port (e.g., 4433)

# Connect to Wi-Fi
print(f"Connecting to {SSID}...")
try:
    wifi.radio.connect(SSID, PASSWORD)
    ip_address = wifi.radio.ipv4_address
    print(f"Connected! IP Address: {ip_address}")
except Exception as e:
    print(f"Wi-Fi Error: {e}")
    time.sleep(10)
    raise SystemExit("Exiting due to Wi-Fi connection failure.")

# Set up socket pool
pool = socketpool.SocketPool(wifi.radio)

def fetch_ssl_data():
    """Connect to the SSL server and fetch JSON data."""
    print(f"Connecting to {SERVER_HOST}:{SERVER_PORT} using SSL...")

    try:
        # Create a socket
        sock = pool.socket()
        
        # Wrap socket with SSL
        ssl_context = ssl.create_default_context()
        ssl_sock = ssl_context.wrap_socket(sock, server_hostname=SERVER_HOST)

        # Connect to the SSL server
        ssl_sock.connect((SERVER_HOST, SERVER_PORT))

        # Receive data
        response = ssl_sock.recv(1024).decode('utf-8')
        ssl_sock.close()  # Close the connection

        # Parse the JSON response
        data = json.loads(response)
        print(f"Received JSON: {data}")
        return data

    except Exception as e:
        print(f"SSL Error: {e}")
        return None

while True:
    try:
        data = fetch_ssl_data()

        if data:
            if "key" in data:
                response = send_key(data["key"])
            elif "string" in data:
                response = send_string(data["string"])
            elif "special" in data:
                response = send_special_combo(data["special"])
            else:
                response = "Invalid request"

            print(response)  # Log the action performed

        time.sleep(5)  # Poll the server every 5 seconds

    except Exception as e:
        print(f"Error: {str(e)}")
        time.sleep(5)
