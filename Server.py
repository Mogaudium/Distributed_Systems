from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy data for example
audio_files = {
    "1": "song1.mp3",
    "2": "song2.mp3",
    # Add more audio files
}

@app.route('/login', methods=['POST'])
def login():
    # Placeholder for login logic
    return jsonify({"message": "Logged in successfully"})

@app.route('/files', methods=['GET'])
def list_files():
    return jsonify(audio_files)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
