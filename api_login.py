from flask import Flask, request, jsonify
import pyodbc
import hashlib

app = Flask(__name__)

# Set up your MS SQL Server connection
server = 'DESKTOP-GMPBUT3\SQLEXPRESS'
database = 'RiskAssessment'

# Function to verify user credentials
def verify_credentials(username, password):
    try:
        # Modify the connection string to use Windows Authentication (Integrated Security)
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};trusted_connection=yes')
        cursor = conn.cursor()
        
        # Retrieve the user's stored password hash and salt
        cursor.execute('SELECT PasswordHash, Salt FROM users WHERE Username = ?', username)
        row = cursor.fetchone()

        if row:
            stored_password_hash = row.PasswordHash
            salt = row.Salt

            # Combine the provided password with the stored salt and hash it
            password_with_salt = password + salt.decode('utf-8')
            hashed_password = hashlib.sha256(password_with_salt.encode()).hexdigest()

            # Compare the computed hash with the stored hash
            if hashed_password == stored_password_hash:
                return True  # Passwords match
        conn.close()
    except Exception as e:
        pass  # Handle database connection or query errors here
    return False

# User login endpoint
# http://127.0.0.1:5000/login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']

        if verify_credentials(username, password):
            response = {'message': 'Login successful'}
        else:
            response = {'error': 'Invalid username or password'}

        return jsonify(response)
    else:
        response = {'error': 'Missing username or password in the request'}
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
