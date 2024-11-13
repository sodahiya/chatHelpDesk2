import socket
import threading

HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 12345
ENCODER = "utf-8"
BYTESIZE = 1024
message_callback = None
user_credentials = {
    "user1": "password123",
    "admin": "adminpass",
    "sodahiya": "1234",
    "harsh" : "56789",
    "nikhil" :  "10111"
}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



def start_server():
    server_socket.bind((HOST_IP, HOST_PORT))
    server_socket.listen()
    print("Server is running...... \nOn")
    print(f"{HOST_IP}:{HOST_PORT}")

    client_socket , client_address = server_socket.accept()
    print(f"Connected to {client_address}")

    #authenticate client
    if not authenticate_client(client_socket):
        print("Authentication failed. Closing connection.")
        client_socket.close()
        return None

    threading.Thread(target=receive_messages, args=(client_socket,),daemon=True).start()

    return client_socket

def authenticate_client(client_socket):
    try:
        # Request and receive username
        username = client_socket.recv(BYTESIZE).decode(ENCODER).strip()

        # Request and receive password
        password = client_socket.recv(BYTESIZE).decode(ENCODER).strip()

        # Validate credentials
        if username in user_credentials and user_credentials[username] == password:
            client_socket.send("Authentication successful.".encode(ENCODER))
            print(f"Client '{username}' authenticated successfully.")
            return True
        else:
            client_socket.send("Authentication failed.".encode(ENCODER))
            print(f"Failed authentication attempt for username '{username}'.")
            return False
    except Exception as e:
        print(f"Error during authentication: {e}")
        return False

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(BYTESIZE).decode(ENCODER)
            if message:
                print(f"Client : {message}")
                if message_callback:
                    message_callback(message)
            else:
                break
        except ConnectionResetError:
            print("Client has disconnected")
            break

    client_socket.close()

def send_message(client_socket,message):
    if client_socket:
        client_socket.send(message.encode(ENCODER))

def set_message_callback(callback):
    global message_callback
    message_callback = callback