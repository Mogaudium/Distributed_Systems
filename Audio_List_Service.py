from flask import Flask, jsonify  
import os  

app = Flask(__name__)  

@app.route('/list-audio')  # Define a route for the Flask application. When the client sends a request to /list-audio, the list_audio function will be called.
def list_audio():
    files = os.listdir('audio_files')  # Use the os.listdir function to get a list of all files in the 'audio_files' directory.
    return jsonify(files)  # The jsonify function is used to convert the list of files to JSON format, which is then returned as the response to the client.

if __name__ == '__main__': 
    app.run(port=5010)  # Start the Flask application on port 5010. 
