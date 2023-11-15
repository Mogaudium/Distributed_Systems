import tkinter as tk
from tkinter import ttk, PhotoImage, messagebox
import requests
from io import BytesIO
import pygame

# Define colors and styles
BACKGROUND_COLOR = "#121212"  # Spotify Dark
FOREGROUND_COLOR = "#FFFFFF"  # White text
ACCENT_COLOR = "#1DB954"     # Spotify Green

def register():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:  # Ensure that username and password are not empty
        response = requests.post('http://localhost:5000/register', data={'username': username, 'password': password})
        print(response.json())  # Print server response
    else:
        print("Username or password is empty")  # Debug print

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:  # Ensure that username and password are not empty
        response = requests.post('http://localhost:5000/login', data={'username': username, 'password': password})
        print(response.json())  # Print server response
    else:
        print("Username or password is empty")  # Debug print

def update_file_list():
    response = requests.get('http://localhost:5000/list-audio')
    if response.status_code == 200:
        file_list = response.json()
        listbox.delete(0, tk.END)  # Clear existing items in the listbox
        for file_name in file_list:
            listbox.insert(tk.END, file_name)
    else:
        print("Failed to retrieve file list")

def stream_and_play():
    selected_file = listbox.get(listbox.curselection())
    url = f'http://localhost:5000/stream/{selected_file}'
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        audio_stream = BytesIO(response.content)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()
    else:
        print("Failed to stream file")

# Initialize the main window
root = tk.Tk()
root.title("Audio Client")
root.geometry("1024x768")  # Spotify's app is typically full-screen; adjust as needed
root.configure(bg=BACKGROUND_COLOR)

# Set the style
style = ttk.Style(root)
style.configure('TButton', font=('Helvetica', 12))
style.configure('TLabel', font=('Helvetica', 12), padding=10)
style.configure('TFrame', background='light grey')

# Main content area
content_frame = tk.Frame(root, bg="#d3d3d3")
content_frame.pack(expand=True, fill=tk.BOTH)

# Left sidebar
sidebar_frame = tk.Frame(root, bg="#1DB954", width=200, height=768)
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

# Playback controls area
playback_frame = tk.Frame(root, bg="#d3d3d3", height=100)
playback_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Login and Registration Frame
auth_frame = ttk.Frame(root, style='TFrame')
auth_frame.pack(pady=10)

username_label = ttk.Label(auth_frame, text="Username", background='light grey')
username_label.pack(side=tk.LEFT)
username_entry = ttk.Entry(auth_frame, width=20)
username_entry.pack(side=tk.LEFT)

password_label = ttk.Label(auth_frame, text="Password", background='light grey')
password_label.pack(side=tk.LEFT)
password_entry = ttk.Entry(auth_frame, width=20, show="*")
password_entry.pack(side=tk.LEFT)

login_button = ttk.Button(auth_frame, text="Login", command=login)
login_button.pack(side=tk.LEFT, padx=5)

register_button = ttk.Button(auth_frame, text="Register", command=register)
register_button.pack(side=tk.LEFT)

# File List Frame
list_frame = ttk.Frame(root, style='TFrame')
list_frame.pack(pady=20)

listbox_label = ttk.Label(list_frame, text="Available Files", background='light grey')
listbox_label.pack()

listbox = tk.Listbox(list_frame, width=50, height=15)
listbox.pack()

update_button = ttk.Button(list_frame, text="Update File List", command=update_file_list)
update_button.pack(pady=10)

play_button = ttk.Button(sidebar_frame, text="Play Selected File", command=stream_and_play)
play_button.pack()

root.mainloop()
