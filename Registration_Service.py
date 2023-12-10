from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'egor' # Or the used password 
app.config['MYSQL_DB'] = 'audio_app'

mysql = MySQL(app)

@app.route('/register', methods=['POST'])  # Define a route for user registration, accepting POST requests
def register():
    # Extract 'username' and 'password' from the request's form data
    username = request.form['username']
    password = request.form['password']

    # Create a new database cursor
    cursor = mysql.connection.cursor()
    # Execute an SQL query to insert the new user into the 'users' table
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    mysql.connection.commit()  # Commit the transaction to the database
    cursor.close()  # Close the cursor

    # Return a JSON response indicating successful registration
    return jsonify({"message": "Registration successful"})

if __name__ == '__main__':
    app.run(port=5003)
