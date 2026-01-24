#!/usr/bin/env python3
"""
Test script to verify Aiven MySQL connection
Run this to test your database connection before deploying
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def test_aiven_connection():
    """Test connection to Aiven MySQL database"""
    
    print("🧪 Testing Aiven MySQL Connection...")
    print("=" * 50)
    
    # Get DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 DATABASE_URL: {database_url}")
    
    try:
        # Parse the DATABASE_URL
        parsed = urlparse(database_url)
        
        db_config = {
            'host': parsed.hostname,
            'user': parsed.username, 
            'password': parsed.password,
            'database': parsed.path[1:] if parsed.path else 'defaultdb',
            'port': parsed.port or 10102,
            'ssl_disabled': False,
            'ssl_ca': 'ca.pem'
        }
        
        print(f"🏠 Host: {db_config['host']}")
        print(f"🔌 Port: {db_config['port']}")
        print(f"👤 User: {db_config['user']}")
        print(f"📊 Database: {db_config['database']}")
        print(f"🔒 SSL Certificate: {db_config['ssl_ca']}")
        
        # Check if ca.pem exists
        if not os.path.exists('ca.pem'):
            print("❌ ca.pem certificate file not found!")
            print("📥 Please download it from Aiven Console > Overview > CA Certificate")
            return False
        
        # Check if ca.pem is real certificate (not placeholder)
        with open('ca.pem', 'r') as f:
            content = f.read()
            if 'PLACEHOLDER' in content or 'Download the CA Certificate' in content:
                print("❌ ca.pem is still a placeholder file!")
                print("📥 Please download the real CA certificate from Aiven Console")
                return False
        
        print("✅ ca.pem certificate file found")
        
        # Attempt connection
        print("\n🔄 Attempting connection...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Connection successful!")
            print(f"📋 MySQL Server version: {db_info}")
            
            # Test a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"🔍 Database version: {version[0]}")
            
            # Check if our database exists
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            db_names = [db[0] for db in databases]
            
            if 'rent_agreements_db' in db_names:
                print("✅ rent_agreements_db database found")
            else:
                print("⚠️ rent_agreements_db database not found")
                print("📝 You need to create it with:")
                print("   CREATE DATABASE rent_agreements_db;")
            
            cursor.close()
            connection.close()
            
            print("\n🎉 Aiven connection test PASSED!")
            return True
            
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print(f"🔢 Error Code: {getattr(e, 'errno', 'Unknown')}")
        print(f"🏷️ SQL State: {getattr(e, 'sqlstate', 'Unknown')}")
        
        # Provide specific troubleshooting
        error_msg = str(e).lower()
        if "ssl" in error_msg:
            print("\n🔒 SSL Issue Troubleshooting:")
            print("1. Download CA certificate from Aiven Console > Overview")
            print("2. Save it as 'ca.pem' in your project root")
            print("3. Make sure the file contains '-----BEGIN CERTIFICATE-----'")
        elif "access denied" in error_msg:
            print("\n🚫 Access Denied Troubleshooting:")
            print("1. Check your Aiven username and password")
            print("2. Verify IP whitelist includes 0.0.0.0/0")
            print("3. Ensure your Aiven service is running")
        elif "connection refused" in error_msg:
            print("\n🔌 Connection Refused Troubleshooting:")
            print("1. Check host and port are correct")
            print("2. Verify your Aiven service is running")
            print("3. Check firewall settings")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def create_database_tables():
    """Create the required database and tables"""
    
    print("\n📋 Creating database and tables...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        parsed = urlparse(database_url)
        
        # Connect to default database first
        db_config = {
            'host': parsed.hostname,
            'user': parsed.username,
            'password': parsed.password,
            'database': 'defaultdb',  # Connect to default first
            'port': parsed.port or 10102,
            'ssl_disabled': False,
            'ssl_ca': 'ca.pem'
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS rent_agreements_db")
        print("✅ Database 'rent_agreements_db' created/verified")
        
        # Switch to our database
        cursor.execute("USE rent_agreements_db")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Table 'users' created/verified")
        
        # Create analysis_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                analysis_result JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ Table 'analysis_history' created/verified")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Error as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Aiven MySQL Connection Test")
    print("=" * 50)
    
    # Test connection
    if test_aiven_connection():
        # If connection works, offer to create tables
        create_tables = input("\n❓ Would you like to create the database tables? (y/n): ")
        if create_tables.lower() in ['y', 'yes']:
            create_database_tables()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")