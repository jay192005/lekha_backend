# app.py (Complete, Updated, and Secured Version)

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import re
import tempfile
from dotenv import load_dotenv
from urllib.parse import urlparse

# --- IMPORTS for handling PDF and DOCX files ---
import PyPDF2
import docx

# --- IMPORTS for OCR (to read scanned documents) ---
# Note: OCR may not be available on serverless platforms like Vercel
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    print("Warning: OCR libraries not available. Scanned PDFs cannot be processed.")
    OCR_AVAILABLE = False

# Load environment variables from a .env file (for your Gemini API Key)
load_dotenv()

# --- CONFIGURATION for OCR tools ---
# Set the path to your Tesseract installation if it's not in your system's PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = os.getenv("POPPLER_PATH", r'C:\Users\JAY GAVALI\Downloads\rent agreement checker\bin')

# --- SSL Certificate Path Configuration ---
# This finds the exact folder where app.py is running (critical for Vercel serverless functions)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_PATH = os.path.join(BASE_DIR, 'ca.pem')

# Import the AI analysis logic from your ai.py file
import ai

app = Flask(__name__)

# Configure CORS for both development and production
allowed_origins = [
    "http://localhost:5000", 
    "http://127.0.0.1:5000", 
    "http://192.168.1.17:5000"
]

# Add production domain if in production
environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    production_domain = os.getenv("PRODUCTION_DOMAIN")
    if production_domain:
        allowed_origins.append(f"https://{production_domain}")
        allowed_origins.append(f"http://{production_domain}")

CORS(app, origins=allowed_origins, 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# --- STATIC FILE ROUTES ---
@app.route('/')
def index():
    """Serve the main index.html file"""
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS, images)"""
    try:
        return app.send_static_file(filename)
    except Exception as e:
        print(f"Static file error: {e}")
        return "File not found", 404

# --- HELPER FUNCTIONS for Validation ---

def is_valid_email(email):
    """Checks if the email format is valid using a simple regex."""
    if not email:
        return False
    # This regex is a common, practical choice for email validation.
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def is_strong_password(password):
    """Checks if the password meets minimum strength requirements."""
    if not password:
        return False
    # For this example, we'll just check for a minimum length of 8 characters.
    return len(password) >= 8

# --- DATABASE CONNECTION MANAGEMENT ---

# --- DATABASE CONNECTION MANAGEMENT ---

def get_db_connection():
    """
    Creates a new database connection using DATABASE_URL or individual parameters.
    Handles both local development and Aiven cloud database with SSL.
    """
    try:
        # Check if we should use local database fallback
        use_local_fallback = os.getenv("USE_LOCAL_DB_FALLBACK", "false").lower() == "true"
        database_url = os.getenv("DATABASE_URL")
        
        # Try Aiven first if DATABASE_URL is provided and not using fallback
        if database_url and not use_local_fallback:
            # Parse the DATABASE_URL for your specific Aiven setup
            parsed = urlparse(database_url)
            
            db_config = {
                'host': parsed.hostname,  # mysql-service-name.aivencloud.com
                'user': parsed.username,  # avnadmin
                'password': parsed.password,  # YOUR_AIVEN_PASSWORD
                'database': parsed.path[1:] if parsed.path else 'defaultdb',  # defaultdb
                'port': parsed.port or 10102,  # PORT_NUMBER
                'autocommit': False,  # We want to control transactions
                'ssl_disabled': False,
                'ssl_ca': CA_PATH,  # Use absolute path for SSL certificate (Vercel compatibility)
                'ssl_verify_cert': True,  # Verify against Aiven's CA
                'ssl_mode': 'REQUIRED'  # Explicitly require SSL
            }
            
            print(f"🔗 Attempting Aiven connection: {db_config['host']}:{db_config['port']}")
            
            try:
                connection = mysql.connector.connect(**db_config)
                if connection.is_connected():
                    db_info = connection.get_server_info()
                    print(f"✅ Aiven connection successful! MySQL version: {db_info}")
                    return connection
            except Error as e:
                print(f"❌ Aiven connection failed: {e}")
                if "ssl" in str(e).lower():
                    print("🔒 SSL Error - falling back to local database")
                # Fall through to local database
        
        # Use local database (fallback or primary)
        db_config = {
            'host': os.getenv("DB_HOST", 'localhost'),
            'user': os.getenv("DB_USER", 'root'),
            'password': os.getenv("DB_PASSWORD"),
            'database': os.getenv("DB_NAME", 'rent_agreements_db'),
            'port': int(os.getenv("DB_PORT", 3306)),
            'autocommit': False
        }
        
        print(f"🏠 Attempting local database connection: {db_config['host']}:{db_config['port']}")
        
        # Create connection
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Local database connection successful! MySQL version: {db_info}")
            return connection
        else:
            print("❌ Database connection failed!")
            return None
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        print(f"🔢 Error Code: {getattr(e, 'errno', 'Unknown')}")
        print(f"🏷️ SQL State: {getattr(e, 'sqlstate', 'Unknown')}")
        
        # Specific error handling for common issues
        error_msg = str(e).lower()
        if "ssl" in error_msg:
            print("🔒 SSL Error: Make sure ca.pem certificate is downloaded and placed in project root")
        elif "access denied" in error_msg:
            print("🚫 Access Denied: Check your database credentials")
        elif "connection refused" in error_msg:
            print("🔌 Connection Refused: Check if MySQL server is running")
        elif "unknown database" in error_msg:
            print("📊 Database not found: Make sure 'rent_agreements_db' database exists")
        
        return None
    except Exception as e:
        print(f"❌ Unexpected database error: {e}")
        return None

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context. This is the best practice for Flask.
    """
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """
    Closes the database connection at the end of the request to free up resources.
    This function is automatically called by Flask.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- User Authentication Endpoints (with Validation) ---
@app.route('/api/register', methods=['POST'])
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

@app.route('/api/login', methods=['POST'])
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

# --- Document Analysis Endpoint ---
@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    try:
        document_text = ""
        
        # Extract text from either pasted content or an uploaded file
        if 'text' in request.form and request.form['text']:
            document_text = request.form['text']
        elif 'file' in request.files:
            file = request.files['file']
            if not file or file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            try:
                if file.filename.lower().endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file.stream)
                    # Check for encrypted PDFs that cannot be read
                    if pdf_reader.is_encrypted:
                        return jsonify({"error": "Cannot process encrypted PDF files."}), 400
                    
                    # First, try the fast text extraction
                    for page in pdf_reader.pages:
                        document_text += page.extract_text() or ""

                    # OCR FALLBACK
                    # If the text is still empty, it's likely a scanned PDF.
                    if not document_text.strip() and OCR_AVAILABLE:
                        print("--- Text extraction failed, falling back to OCR. ---")
                        # We need to save the file temporarily to use its path
                        file.stream.seek(0)
                        
                        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                        try:
                            with os.fdopen(fd, 'wb') as tmp:
                                tmp.write(file.stream.read())
                            
                            images = convert_from_path(temp_path, poppler_path=POPPLER_PATH)
                            for image in images:
                                document_text += pytesseract.image_to_string(image) + "\n"
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                    elif not document_text.strip() and not OCR_AVAILABLE:
                        return jsonify({"error": "This appears to be a scanned PDF. OCR is not available on this server. Please convert to text format or use a different document."}), 400

                elif file.filename.lower().endswith('.docx'):
                    doc = docx.Document(file.stream)
                    document_text = '\n'.join([para.text for para in doc.paragraphs])
                else:  # Assume .txt or other plain text formats
                    document_text = file.read().decode('utf-8')
            except Exception as e:
                # Provide a more user-friendly error for corrupted files
                print(f"File Read Error: {e}")
                return jsonify({"error": "Could not read the uploaded file. It may be corrupted or in an unsupported format."}), 400
        
        if not document_text.strip():
            return jsonify({"error": "Could not extract any text from the document. It might be empty or a scanned image."}), 400

        state = request.form.get('state', '')
        email = request.form.get('email', None)

        # Step 1: Get the analysis from your AI module (ai.py)
        preliminary_findings = ai.analyze_text_with_rules(document_text)
        gemini_result = ai.analyze_with_gemini(document_text, preliminary_findings, state)
        
        if "error" in gemini_result:
            return jsonify(gemini_result), 500

        # Step 2: Create the complete final result object to be sent and saved
        final_result = gemini_result
        final_result['redFlagsCount'] = len(gemini_result.get('redFlags', []))
        final_result['fairClausesCount'] = len(gemini_result.get('fairClauses', []))

        # Step 3: Save the complete result to the database if the user is logged in
        if email:
            db = get_db()
            if db:
                cursor = db.cursor()
                try:
                    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                    user = cursor.fetchone()
                    if user:
                        user_id = user[0]  # The user ID
                        # Convert the final result dictionary to a JSON string for storage.
                        result_json_string = json.dumps(final_result)
                        
                        cursor.execute(
                            "INSERT INTO analysis_history (user_id, analysis_result) VALUES (%s, %s)",
                            (user_id, result_json_string)
                        )
                        db.commit()
                        print(f"Analysis saved for user_id: {user_id}")
                except Error as e:
                    db.rollback()
                    print(f"Error saving analysis to DB: {e}")
                finally:
                    cursor.close()

        # Step 4: Return the complete result to the frontend
        return jsonify(final_result)
        
    except Exception as e:
        print(f"Unexpected analysis error: {e}")
        return jsonify({"error": "An unexpected error occurred during analysis"}), 500

# --- Get Analysis History Endpoint ---
@app.route('/api/history/<email>', methods=['GET'])
def get_history(email):
    try:
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email format"}), 400
            
        db = get_db()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT h.id, h.analysis_result, h.created_at
                FROM analysis_history h
                JOIN users u ON h.user_id = u.id
                WHERE u.email = %s
                ORDER BY h.created_at DESC
            """
            cursor.execute(query, (email,))
            history = cursor.fetchall()
            
            # Format the date and parse the analysis_result JSON string into a dictionary
            for item in history:
                item['created_at'] = item['created_at'].isoformat()
                try:
                    item['analysis_result'] = json.loads(item['analysis_result'])
                except json.JSONDecodeError:
                    item['analysis_result'] = {}

            return jsonify(history), 200
        except Error as e:
            print(f"History Fetch Error: {e}")
            return jsonify({"error": "An internal error occurred while fetching history."}), 500
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Unexpected history error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# --- Data Management Endpoints ---

@app.route('/api/delete-data', methods=['POST'])
def delete_data():
    """
    Deletes data from specified table based on the request.
    Supports both DELETE (with conditions) and TRUNCATE (all data) operations.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        table_name = data.get('table')
        operation = data.get('operation', 'delete')  # 'delete' or 'truncate'
        conditions = data.get('conditions', {})  # For DELETE operations
        
        # Validate table name (security measure)
        allowed_tables = ['users', 'analysis_history']
        if table_name not in allowed_tables:
            return jsonify({"error": f"Table '{table_name}' is not allowed for deletion"}), 400
        
        # Get database connection
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        try:
            if operation.lower() == 'truncate':
                # TRUNCATE removes all data from table
                query = f"TRUNCATE TABLE {table_name}"
                cursor.execute(query)
                affected_rows = "all"
                
            elif operation.lower() == 'delete':
                # DELETE with conditions
                if not conditions:
                    return jsonify({"error": "DELETE operation requires conditions"}), 400
                
                # Build WHERE clause safely
                where_conditions = []
                values = []
                
                for column, value in conditions.items():
                    # Basic column name validation (prevent SQL injection)
                    if not column.replace('_', '').isalnum():
                        return jsonify({"error": f"Invalid column name: {column}"}), 400
                    
                    where_conditions.append(f"{column} = %s")
                    values.append(value)
                
                where_clause = " AND ".join(where_conditions)
                query = f"DELETE FROM {table_name} WHERE {where_clause}"
                
                cursor.execute(query, values)
                affected_rows = cursor.rowcount
                
            else:
                return jsonify({"error": "Invalid operation. Use 'delete' or 'truncate'"}), 400
            
            # CRITICAL: Commit the transaction
            connection.commit()
            
            print(f"✅ Successfully executed {operation.upper()} on {table_name}. Affected rows: {affected_rows}")
            
            return jsonify({
                "message": f"Successfully {operation}d data from {table_name}",
                "table": table_name,
                "operation": operation,
                "affected_rows": affected_rows
            }), 200
            
        except Error as e:
            # Rollback on error
            connection.rollback()
            print(f"❌ Database operation error: {e}")
            return jsonify({"error": f"Database operation failed: {str(e)}"}), 500
            
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        print(f"❌ Unexpected error in delete_data: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_analysis_history():
    """
    Convenience endpoint to clear analysis history for a specific user or all users.
    """
    try:
        data = request.get_json()
        email = data.get('email') if data else None
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        try:
            if email:
                # Clear history for specific user
                cursor.execute("""
                    DELETE h FROM analysis_history h 
                    JOIN users u ON h.user_id = u.id 
                    WHERE u.email = %s
                """, (email,))
                affected_rows = cursor.rowcount
                message = f"Cleared analysis history for user: {email}"
            else:
                # Clear all analysis history
                cursor.execute("DELETE FROM analysis_history")
                affected_rows = cursor.rowcount
                message = "Cleared all analysis history"
            
            # CRITICAL: Commit the transaction
            connection.commit()
            
            print(f"✅ {message}. Affected rows: {affected_rows}")
            
            return jsonify({
                "message": message,
                "affected_rows": affected_rows
            }), 200
            
        except Error as e:
            connection.rollback()
            print(f"❌ Error clearing history: {e}")
            return jsonify({"error": f"Failed to clear history: {str(e)}"}), 500
            
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        print(f"❌ Unexpected error in clear_history: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint that tests database connectivity"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({
                "status": "unhealthy", 
                "database": "disconnected",
                "error": "Could not establish database connection"
            }), 500
        
        # Test the connection with a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                "status": "healthy", 
                "database": "connected",
                "message": "All systems operational"
            }), 200
        else:
            return jsonify({
                "status": "unhealthy", 
                "database": "query_failed"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "error": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# This is the standard entry point for running a Flask application.
if __name__ == '__main__':
    # debug=True automatically reloads the server when you make changes.
    # Turn this off for production deployment.
    app.run(host='0.0.0.0', port=5000, debug=True)