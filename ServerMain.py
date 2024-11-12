import tkinter as tk
import ttkbootstrap as ttk
import threading
import simpleServer

window = ttk.Window(themename="cosmo")
window.title('Helpdesk Server')
window.geometry('800x600')

# Global Variables
chat_frame = None
client_socket = None
canvas = None
scrollbar = None

def start_server():
    print("Starting server...")
    start_server_button.config(text="Server is Running", state="disabled")

    # Display the server's IP and Port
    IP_label = ttk.Label(master=window, text=f"Server Running On {simpleServer.HOST_IP} : {simpleServer.HOST_PORT}", bootstyle="dark")
    IP_label.pack()

    # Setup chat frame with a canvas and a scrollbar
    global chat_frame, chat_message_frame, canvas, scrollbar
    chat_frame = ttk.Frame(master=window, borderwidth=10)
    chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(chat_frame)
    scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configure scrolling
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Make the scrollable frame available for message display
    chat_message_frame = scrollable_frame

    # Input and Send Button
    send_frame = ttk.Frame(master=window)
    send_frame.pack(fill="x", padx=10, pady=10)
    global chat_entry
    chat_entry = ttk.Entry(master=send_frame)
    chat_entry.pack(side="left", fill="x", expand=True, padx=10)
    chat_entry.bind("<Return>", lambda event: send_message())

    send_button = ttk.Button(master=send_frame, text="Send", command=send_message, bootstyle="primary")
    send_button.pack(side="left", padx=10)

    simpleServer.set_message_callback(display_message_client)

    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server_thread)
    server_thread.daemon = True  # This closes the thread when the window closes
    server_thread.start()

def start_server_thread():
    global client_socket
    client_socket = simpleServer.start_server()

def send_message():
    message = chat_entry.get()
    if message and client_socket:
        simpleServer.send_message(client_socket, message)
        display_message_server(message)
        chat_entry.delete(0, tk.END)

def display_message_client(message):
    """Display a new message from the client."""
    message_label = ttk.Label(master=chat_message_frame, text=f"Client : {message}", bootstyle="info")
    message_label.pack(fill="x", padx=10, pady=5, anchor="w")
    # Auto-scroll to the bottom
    canvas.yview_moveto(1)

def display_message_server(message):
    """Display a new message from the server."""
    message_label = ttk.Label(master=chat_message_frame, text=f"Server : {message}", bootstyle="secondary")
    message_label.pack(fill="x", padx=10, pady=5, anchor="w")
    # Auto-scroll to the bottom
    canvas.yview_moveto(1)

header_label = ttk.Label(master=window, text="Helpdesk\nServer Control Panel", font=("Helvetica", 24, "bold"), bootstyle="dark")
header_label.pack(pady=30)

start_server_button = ttk.Button(master=window, text="Start Server", command=start_server, bootstyle="success-outline")
start_server_button.pack(pady=10)

window.mainloop()
