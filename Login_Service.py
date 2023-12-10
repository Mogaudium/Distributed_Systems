def login_user(mysql, username, password):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    return {"message": "Logged in successfully"} if user else {"message": "Invalid credentials"}, 200 if user else 401
