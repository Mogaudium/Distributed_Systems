import sys
import requests
import subprocess
import pkg_resources
from flask import Flask, jsonify, request, redirect

# Function to install missing Python dependencies
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


# Forward the registration request to the registration microservice
@app.route('/register', methods=['POST'])
def register():
    response = requests.post('http://localhost:5003/register', data=request.form)
    return jsonify(response.json()), response.status_code

# Forward the login request to the login microservice
@app.route('/login', methods=['POST'])
def login():
    response = requests.post('http://localhost:5004/login', data=request.form)
    return jsonify(response.json()), response.status_code

# Send a request to the audio listing microservice
@app.route('/list-audio')
def list_audio():
    try:
        response = requests.get('http://localhost:5010/list-audio')  # Check the response status
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Microservice error"}), response.status_code
    except requests.exceptions.RequestException as e:
        # Log connection errors
        app.logger.error(f"Microservice connection error: {str(e)}")
        return jsonify({"error": "Microservice connection error"}), 500

# Redirect the request to the audio streaming microservice
@app.route('/stream/<filename>', methods=['GET'])
def stream_audio(filename):
    return redirect(f'http://localhost:5020/stream/{filename}')

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(debug=True, port=port)
