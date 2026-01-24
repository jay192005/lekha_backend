"""
Authentication routes for user registration and login
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error
from ..database import get_db
from ..utils import is_valid_email, is_strong_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')

        # Backend Validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        if not is_valid_email(email):
            return jsonify({"error": "Please enter a valid email address"}), 400
        if not is_strong_password(password):
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        db = get_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = db.cursor(dictionary=True)
        
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "An account with this email already exists"}), 409

            # Create new user
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, password_hash))
            
            new_user_id = cursor.lastrowid
            db.commit()
            
            # Return user info to automatically log them in on the frontend
            return jsonify({
                "message": "Account created successfully!",
                "email": email,
                "id": new_user_id
            }), 201
            
        except Error as e:
            db.rollback()
            print(f"Registration Error: {e}")
            if hasattr(e, 'errno'):
                print(f"Error Code: {e.errno}")
            if hasattr(e, 'sqlstate'):
                print(f"SQL State: {e.sqlstate}")
            return jsonify({"error": "An internal error occurred during registration."}), 500
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Unexpected registration error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db = get_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                return jsonify({
                    "message": "Login successful!",
                    "email": user['email'],
                    "id": user['id']
                }), 200
            else:
                # Use a generic error message for security
                return jsonify({"error": "Invalid credentials"}), 401
        except Error as e:
            print(f"Login Error: {e}")
            return jsonify({"error": "An internal error occurred during login."}), 500
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Unexpected login error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500