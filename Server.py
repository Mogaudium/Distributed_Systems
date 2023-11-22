import os
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename, safe_join
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor'
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

# Register method
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']  
    print("Received username:", username, "and password:", password)  
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Registration successful"})

# Login method
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({"message": "Logged in successfully"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
# List audio files method
@app.route('/list-audio')
def list_audio():
    files = os.listdir('audio_files')  # Assuming 'audio_files' is your directory
    return jsonify(files)

# Stream the selected audio file method
@app.route('/stream/<filename>', methods=['GET'])
def stream_audio(filename):
    directory = safe_join(app.root_path, 'audio_files')
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
