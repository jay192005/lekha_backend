"""
Document analysis routes
"""
from flask import Blueprint, request, jsonify
import json
import tempfile
import os
from mysql.connector import Error

# Document processing imports
import PyPDF2
import docx
from pdf2image import convert_from_path
import pytesseract

from ..database import get_db
from ..utils import is_valid_email
from .. import ai
from ..config import Config

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analyze', methods=['POST'])
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
                    if not document_text.strip():
                        print("--- Text extraction failed, falling back to OCR. ---")
                        # We need to save the file temporarily to use its path
                        file.stream.seek(0)
                        
                        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
                        try:
                            with os.fdopen(fd, 'wb') as tmp:
                                tmp.write(file.stream.read())
                            
                            images = convert_from_path(temp_path, poppler_path=Config.POPPLER_PATH)
                            for image in images:
                                document_text += pytesseract.image_to_string(image) + "\n"
                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

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

@analysis_bp.route('/api/history/<email>', methods=['GET'])
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