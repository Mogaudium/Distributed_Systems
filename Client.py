import tkinter as tk
import requests
import pygame
from io import BytesIO

def login():
    # Login to the server
    response = requests.post('http://localhost:5000/login', data={"username": "user1", "password": "password1"})
    print(response.json())

def get_file_list():
    # Get the list of files from the server
    response = requests.get('http://localhost:5000/files')
    print(response.json())

def download_and_play(file_name):
    response = requests.get(f'http://localhost:5000/file/{file_name}')
    if response.status_code == 200:
        audio_data = BytesIO(response.content)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_data)
        pygame.mixer.music.play()
    else:
        print("Failed to download file")

root = tk.Tk()
root.title("Audio Client")

# Login Fields
username_label = tk.Label(root, text="Username")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="Password")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

list_files_button = tk.Button(root, text="List Files", command=get_file_list)
list_files_button.pack()

play_button = tk.Button(root, text="Play File", command=lambda: download_and_play('path/to/song1.mp3'))
play_button.pack()

root.mainloop()
