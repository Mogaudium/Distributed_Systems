import tkinter as tk
import requests

def login():
    # Login to the server
    response = requests.post('http://localhost:5000/login', data={"username": "user", "password": "pass"})
    print(response.json())

def get_file_list():
    # Get the list of files from the server
    response = requests.get('http://localhost:5000/files')
    print(response.json())

root = tk.Tk()
root.title("Audio Client")

login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

list_files_button = tk.Button(root, text="List Files", command=get_file_list)
list_files_button.pack()

root.mainloop()
