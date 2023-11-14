from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Dummy user data
users = {
    "user1": "password1",
    "user2": "password2"
}

# Dummy audio file data
audio_files = {
    "1": "song1.mp3",
    "2": "song2.mp3"
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        return jsonify({"message": "Logged in successfully"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/files', methods=['GET'])
def list_files():
    return jsonify(audio_files)

@app.route('/file/<filename>', methods=['GET'])
def get_file(filename):
    # Assuming files are stored in a directory named 'audio_files'
    return send_from_directory('audio_files', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
