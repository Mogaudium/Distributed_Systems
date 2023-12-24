from flask import Flask, send_from_directory, request
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AudioStreamService')

# Configure a log file with rotation to manage log size
file_handler = RotatingFileHandler('audio_stream_service.log', maxBytes=10000, backupCount=1) # The log file rotates after reaching a size of 10000 bytes, keeping one backup file
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

@app.route('/stream/<filename>', methods=['GET']) # Define a route with a variable part <filename>. This route listens for GET requests.
def stream_audio(filename):
    try:
        directory = 'audio_files' # Specify the directory where audio files are stored.
        client_ip = request.remote_addr  # Get client's IP address

        logger.info(f'Requested to stream audio file: {filename} from IP: {client_ip}') # Log the requested audio file and client IP in audio_stream_service.log
        return send_from_directory(directory, filename) # The send_from_directory function sends a file from the specified directory to the client.
    except Exception as e:
        logger.error(f'Error streaming audio file: {filename} from IP: {client_ip}, Error: {e}') # Log the streaming audio file error in audio_stream_service.log
        return f"Error streaming audio file: {filename}", 500

if __name__ == '__main__':
    app.run(host = '192.168.1.6', port=5020)
