from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor'  
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

@app.route('/login', methods=['POST'])  # Define a route for the login endpoint, allowing POST requests
def login():
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
        # If the user exists, return a success message
        return jsonify({"message": "Logged in successfully"})
    else:
        # If no user record was found, return an error message with a 401 Unauthorized status code
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(port=5004)
