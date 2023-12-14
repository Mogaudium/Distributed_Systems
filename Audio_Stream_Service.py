from flask import Flask, send_from_directory
import logging
from logging.handlers import RotatingFileHandler # RotatingFileHandler is used in order to avoid the log file becoming too large.

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AudioStreamService')

# Log to a file
file_handler = RotatingFileHandler('audio_stream_service.log', maxBytes=10000, backupCount=1) # When the log file reaches 10000 bytes, a new file will be started.
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

@app.route('/stream/<filename>', methods=['GET'])  # Define a route with a variable part <filename>. This route listens for GET requests.
def stream_audio(filename):
    try:
        directory = 'audio_files'  # Specify the directory where audio files are stored.
        logger.info(f'Requested to stream audio file: {filename}') # Log the requested audio file in audio_stream_service.log
        return send_from_directory(directory, filename)  # The send_from_directory function sends a file from the specified directory to the client.
    except Exception as e:
        logger.error(f'Error streaming audio file: {filename}, Error: {e}') # Log the streaming audio file error in audio_stream_service.log
        return f"Error streaming audio file: {filename}", 500 # Return the error

if __name__ == '__main__':
    app.run(port=5020)
