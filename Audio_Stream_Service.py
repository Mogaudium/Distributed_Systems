from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/stream/<filename>', methods=['GET'])  # Define a route with a variable part <filename>. This route listens for GET requests.
def stream_audio(filename):
    directory = 'audio_files'  # Specify the directory where audio files are stored.
    return send_from_directory(directory, filename)  # The send_from_directory function sends a file from the specified directory to the client.

if __name__ == '__main__':
    app.run(port=5020)
