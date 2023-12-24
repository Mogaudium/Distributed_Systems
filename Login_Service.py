from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import logging
from logging.handlers import RotatingFileHandler
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LoginService')

# Configure a log file with rotation to manage log size
file_handler = RotatingFileHandler('login_service.log', maxBytes=10000, backupCount=1) # The log file rotates after reaching a size of 10000 bytes, keeping one backup file
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor' # Replace with the actual password of your SQL
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

@app.route('/login', methods=['POST'])
def login():
    try:
        # Extract username and password from the form data
        username = request.form['username']
        password = request.form['password']

        # Get the hashed version of the password for logging
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Get the client's IP address
        client_ip = request.remote_addr

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Log the username, hashed password, and client IP
            logger.info(f"Login attempt for user: {username}, Password Hash: {hashed_password}, IP: {client_ip}")

            return jsonify({"message": "Logged in successfully"})
        else:
            logger.warning(f"Failed login attempt for user: {username}, Password Hash: {hashed_password}, IP: {client_ip}")
            return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5004)
