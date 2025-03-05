import socket
import ssl
import json

HOST = "0.0.0.0"  # Listen on all network interfaces
PORT = 4433  # SSL port
CERT_FILE = "cert.pem"  # Path to SSL certificate
KEY_FILE = "key.pem"  # Path to SSL private key

def handle_client(client_socket):
    """Send a JSON command to the client."""
    try:
        # Receive optional request (not required for one-way comms)
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received request: {request}")

        # Example JSON payload to send
        json_response = json.dumps({"string": "Hello, World!"})
        
        # Send JSON response
        client_socket.send(json_response.encode('utf-8'))
        print("Sent JSON command to client.")

    except Exception as e:
        print(f"Error handling client: {e}")

    finally:
        client_socket.close()

# Create SSL Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)  # Listen for incoming connections

# Wrap socket with SSL
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

print(f"SSL Server listening on port {PORT}...")

while True:
    try:
        # Accept client connection
        client_sock, addr = server_socket.accept()
        secure_sock = ssl_context.wrap_socket(client_sock, server_side=True)
        print(f"Client connected from {addr}")

        # Handle client request
        handle_client(secure_sock)

    except Exception as e:
        print(f"Server error: {e}")
