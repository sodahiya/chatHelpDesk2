import tkinter as tk
import ttkbootstrap as ttk
import simpleClient
import threading
import re

window = ttk.Window(themename="cosmo")
window.title('Helpdesk Client')
window.geometry('800x600')

chat_frame = None
chat_message_frame = None
message_entry = None
canvas = None
scrollbar = None

def filter_message(message):
    # Define a set of cuss words (expand as needed)
    cuss_words = {"badword1", "badword2", "cussword3"}  # Replace with actual cuss words

    # Split the paragraph into words using whitespace
    words = message.split()

    # Regular expression patterns to identify phone numbers and email addresses
    phone_pattern = re.compile(r'(\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b)')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Iterate over each word and replace cuss words, phone numbers, and email addresses
    censored_words = []
    for word in words:
        if phone_pattern.search(word):
            censored_word = '*' * len(word)
        elif email_pattern.search(word):
            censored_word = '*' * len(word)
        else:
            stripped_word = ''.join(char for char in word if char.isalnum()).lower()
            if stripped_word in cuss_words:
                censored_word = '*' * len(stripped_word)
                censored_word = word.replace(stripped_word, censored_word)
            else:
                censored_word = word

        censored_words.append(censored_word)

    # Rejoin the words to form the censored paragraph
    censored_paragraph = ' '.join(censored_words)
    return censored_paragraph

def display_message_server(message):
    """Displays a message from the server."""
    message_label = ttk.Label(master=chat_message_frame, text=f"Server : {message}", bootstyle="info")
    message_label.pack(fill="x", padx=10, pady=5, anchor="w")
    canvas.yview_moveto(1)

def display_message_client(message):
    """Displays a message from the client."""
    message_label = ttk.Label(master=chat_message_frame, text=f"Client : {message}", bootstyle="secondary")
    message_label.pack(fill="x", padx=10, pady=5, anchor="w")
    canvas.yview_moveto(1)

def connect_client():
    """Connects to the server."""
    dest_ip = DEST_IP.get()
    dest_port = DEST_PORT.get()

    if not simpleClient.connect_client(dest_ip, dest_port, display_message_server):
        print("Unable to connect to the server. Please check IP/Port.")
        return

    user_name = USER_NAME.get()
    user_pass = USER_PASS.get()
    threading.Thread(target=simpleClient.handle_authentication, args=(user_name, user_pass), daemon=True).start()

    print("Connected")
    client_connect_button.config(text="Connected", state="disabled")
    DEST_PORT_entry.config(state="disabled")
    DEST_IP_entry.config(state="disabled")

    global chat_frame, chat_message_frame, canvas, scrollbar
    chat_frame = ttk.Frame(master=window, borderwidth=10)
    chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(chat_frame)
    scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    chat_message_frame = scrollable_frame

    # Input and Send Button
    send_frame = ttk.Frame(master=window)
    send_frame.pack(fill="x", padx=10, pady=10)
    global message_entry
    message_entry = ttk.Entry(master=send_frame)
    message_entry.pack(side="left", fill="x", expand=True, padx=10)
    message_entry.bind("<Return>", lambda event: send_message())

    send_button = ttk.Button(master=send_frame, text="Send", command=send_message, bootstyle="primary")
    send_button.pack(side="left", padx=10)

def send_message():
    """Sends a message."""
    message = filter_message(message_entry.get())
    if message:
        simpleClient.send_message(message)
        display_message_client(message)
        message_entry.delete(0, tk.END)

def on_closing():
    """Handles window closing."""
    simpleClient.disconnect_client()
    window.destroy()

header_label = ttk.Label(master=window, text="Helpdesk\nClient Control Panel", font=("Helvetica", 24, "bold"), bootstyle="dark")
header_label.pack(pady=30)

connect_frame = ttk.Frame(master=window)
connect_frame.pack()

user_frame = ttk.Frame(master=window)
user_frame.pack()

DEST_IP = tk.StringVar(value="IP ADDRESS")
DEST_IP_entry = ttk.Entry(master=connect_frame, textvariable=DEST_IP)
DEST_IP_entry.pack(side="left", padx=10, pady=10)

label = ttk.Label(master=connect_frame, text=":")
label.pack(side="left", padx=10, pady=10)

DEST_PORT = tk.StringVar(value="12345")
DEST_PORT_entry = ttk.Entry(master=connect_frame, textvariable=DEST_PORT)
DEST_PORT_entry.pack(side="left", padx=10, pady=10)

USER_NAME = tk.StringVar(value="admin")
USER_NAME_entry = ttk.Entry(master=user_frame, textvariable=USER_NAME)
USER_NAME_entry.pack(side="left", padx=10, pady=10)

USER_PASS = tk.StringVar(value="adminpass")
USER_PASS_entry = ttk.Entry(master=user_frame, textvariable=USER_PASS, show="*")
USER_PASS_entry.pack(side="left", padx=10, pady=10)

client_connect_button = ttk.Button(master=user_frame, width=20, text='Connect', command=connect_client, bootstyle="success-outline")
client_connect_button.pack(side="left", pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
