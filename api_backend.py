from flask import Flask, request, jsonify
import pyodbc
import hashlib
import secrets

app = Flask(__name__)

# Set up your MS SQL Server connection
server = 'DESKTOP-GMPBUT3\SQLEXPRESS'
database = 'RiskAssessment'

# User registration endpoint
@app.route('/register', methods=['POST'])

def register():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']
        email = data['email']
        firstname = data['firstname']
        lastname = data['lastname']

        # Generate a random salt
        salt = secrets.token_bytes(16)

        # Combine the password and salt
        password_with_salt = password + salt.hex()

        # Hash the combined password with salt using SHA-256
        hashed_password = hashlib.sha256(password_with_salt.encode()).hexdigest()

        # For security, you should hash and salt the password before storing it in the database

        # Modify the connection string to use Windows Authentication (Integrated Security)
        try:
            conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};trusted_connection=yes')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (Username, PasswordHash, Salt, Email, FirstName, LastName)  VALUES (?, ?, ?, ?, ?, ?)', 
                           (username, hashed_password, salt, email, firstname, lastname))
            conn.commit()
            conn.close()
        except Exception as e:
            print('error ',e)
            response = {'error': 'An error occurred while inserting data into the database'}
            return jsonify(response)
        response = {'message': 'User registered successfully'}
        return jsonify(response)
    else:
        # Return an error response if the required data is not provided
        response = {'error': 'Missing username or password in the request'}
        return jsonify(response)
    
def verify_credentials(username, password):
    try:
        # Modify the connection string to use Windows Authentication (Integrated Security)
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};trusted_connection=yes')
        cursor = conn.cursor()
        
        # Retrieve the user's stored password hash and salt
        print('inside verify_credentials')

        try:
            cursor.execute('SELECT PasswordHash, Salt FROM users WHERE Username = ?', username)
            row = cursor.fetchone()
        except Exception as e:
            print('error ',e)

        if row:
            print('inside row')
            stored_password_hash = row.PasswordHash
            salt = row.Salt

            # Combine the provided password with the stored salt and hash it
            password_with_salt = password + salt.hex()
            hashed_password = hashlib.sha256(password_with_salt.encode()).hexdigest()
            print('hashed_password ',hashed_password)

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