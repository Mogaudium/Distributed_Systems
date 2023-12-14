from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import logging
from logging.handlers import RotatingFileHandler # RotatingFileHandler is used in order to avoid the log file becoming too large.

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LoginService')

# Log to a file
file_handler = RotatingFileHandler('login_service.log', maxBytes=10000, backupCount=1) # When the log file reaches 10000 bytes, a new file will be started.
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor' # Or the used password 
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

@app.route('/login', methods=['POST'])  # Define a route for the login endpoint, allowing POST requests
def login():
    try:
        # Extract username and password from the form data sent in the request
        username = request.form['username']
        password = request.form['password']

        # Create a new database cursor
        cursor = mysql.connection.cursor()
        # Execute a SQL query to check if the user exists with the given username and password
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()  # Fetch one record from the query result
        cursor.close()  # Close the cursor

        # Check if a user record was found
        if user:
            logger.info("Login attempt for user: " + request.form['username'])

            # If the user exists, return a success message
            return jsonify({"message": "Logged in successfully"})
        else:
            # If no user record was found, return an error message with a 401 Unauthorized status code
            return jsonify({"message": "Invalid credentials"}), 401
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": str(e)}), 500

            
        

if __name__ == '__main__':
    app.run(port=5004)
