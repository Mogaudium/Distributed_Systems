from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import logging
from logging.handlers import RotatingFileHandler # RotatingFileHandler is used in order to avoid the log file becoming too large.

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RegistrationService')

# Log to a file
file_handler = RotatingFileHandler('registration_service.log', maxBytes=10000, backupCount=1) # When the log file reaches 10000 bytes, a new file will be started.
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

@app.route('/register', methods=['POST'])  # Define a route for user registration, accepting POST requests
def register():
    try:
        # Extract 'username' and 'password' from the request's form data
        username = request.form['username']
        password = request.form['password']

        # Create a new database cursor
        cursor = mysql.connection.cursor()
        # Execute an SQL query to insert the new user into the 'users' table
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()  # Commit the transaction to the database
        cursor.close()  # Close the cursor

        logger.info("Registration attempt for user: " + request.form['username'])

        # Return a JSON response indicating successful registration
        return jsonify({"message": "Registration successful"})
    
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5003)
