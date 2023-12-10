import sys
import subprocess
import pkg_resources
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import Registration_Service
import Login_Service
import Audio_List_Service
import Audio_Stream_Service

def install_dependencies():
    required = {'Flask', 'flask_mysqldb', 'Werkzeug'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("Installing missing dependencies...")
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', *missing])

install_dependencies()

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor'
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    result = Registration_Service.register_user(mysql, username, password)
    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    message, status_code = Login_Service.login_user(mysql, username, password)
    return jsonify(message), status_code

@app.route('/list-audio')
def list_audio():
    files = Audio_List_Service.list_audio_files('audio_files')
    return jsonify(files)

@app.route('/stream/<filename>', methods=['GET'])
def stream_audio(filename):
    return Audio_Stream_Service.stream_audio_file(app, filename)

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(debug=True, port=port)
