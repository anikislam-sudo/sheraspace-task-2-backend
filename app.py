from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
CORS(app)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sheraspace'

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
    return 'Server is running'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    linkedin_url = data['linkedin_url']

    try:
        cursor = mysql.connection.cursor()

        # Check if LinkedIn URL already exists
        cursor.execute("SELECT * FROM users WHERE linkedin_url = %s", (linkedin_url,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'error': 'LinkedIn URL already exists'}), 400

        # Hash the password before storing it in the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (username, email, password, linkedin_url) VALUES (%s, %s, %s, %s)",
                       (username, email, hashed_password, linkedin_url))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, email, linkedin_url FROM users")
        users = cursor.fetchall()
        cursor.close()

        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'linkedin_url': user[3]
            })

        return jsonify(users_list), 200

    except Exception as e:
        print(e)  # Log the exception
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)