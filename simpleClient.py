import socket
import threading

DEST_PORT = 12345
ENCODER = "utf-8"
BYTESIZE = 1024
client_socket = None
stop_receiving = False

def send_message(message):
    """Sends a message to the server."""
    if client_socket:
        try:
            client_socket.send(message.encode(ENCODER))
        except Exception as e:
            print(f"Error sending message: {e}")

def receive_messages(callback):
    """Receives messages from the server."""
    global stop_receiving
    while not stop_receiving:
        try:
            message = client_socket.recv(BYTESIZE).decode(ENCODER)
            if not message:
                break
            callback(message)
        except Exception as e:
            if not stop_receiving:
                print(f"Error receiving message: {e}")
            break

def connect_client(DEST_IP, DEST_PORT, message_callback):
    """Connects to the server."""
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((DEST_IP, int(DEST_PORT)))
        print("Connected to the server")
        # Start a thread for receiving messages
        threading.Thread(target=receive_messages, args=(message_callback,), daemon=True).start()
        return True
    except socket.error as e:
        print(f"Failed to connect to {DEST_IP}:{DEST_PORT} - {e}")
        if client_socket:
            client_socket.close()
        return False

def handle_authentication(username, password):
    """Sends username and password for authentication."""
    try:
        client_socket.send(username.encode(ENCODER))
        client_socket.send(password.encode(ENCODER))
        result = client_socket.recv(BYTESIZE).decode(ENCODER)
        print(result)
        if "failed" in result.lower():
            print("Exiting due to failed authentication.")
            disconnect_client()
    except Exception as e:
        print(f"Error during authentication: {e}")
        disconnect_client()

def disconnect_client():
    """Closes the client connection."""
    global stop_receiving
    stop_receiving = True
    if client_socket:
        client_socket.close()
    print("Disconnected from the server.")
