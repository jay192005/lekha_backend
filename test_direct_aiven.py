#!/usr/bin/env python3
"""
Direct Aiven connection test with detailed error reporting
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def test_direct_aiven():
    """Test direct connection to Aiven with detailed error reporting"""
    
    print("🔗 Testing Direct Aiven Connection...")
    print("=" * 50)
    
    try:
        # Load connection parameters from environment variables
        config = {
            'host': os.getenv('DB_HOST', 'your-mysql-host.aivencloud.com'),
            'port': int(os.getenv('DB_PORT', 10102)),
            'user': os.getenv('DB_USER', 'avnadmin'),
            'password': os.getenv('DB_PASSWORD', 'your-password'),
            'database': os.getenv('DB_NAME', 'defaultdb'),
            'ssl_disabled': False,
            'ssl_ca': 'ca.pem',
            'connect_timeout': 30,
            'autocommit': False
        }
        
        print(f"🏠 Host: {config['host']}")
        print(f"🔌 Port: {config['port']}")
        print(f"👤 User: {config['user']}")
        print(f"📊 Database: {config['database']}")
        print(f"🔒 SSL CA: {config['ssl_ca']}")
        
        print("\n🔄 Attempting connection...")
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ SUCCESS! Connected to Aiven MySQL")
            print(f"📋 Server version: {db_info}")
            
            # Test a query
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION(), DATABASE(), USER()")
            result = cursor.fetchone()
            
            print(f"🔍 Version: {result[0]}")
            print(f"📊 Current DB: {result[1]}")
            print(f"👤 Current User: {result[2]}")
            
            cursor.close()
            connection.close()
            
            return True
            
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print(f"🔢 Error Code: {getattr(e, 'errno', 'Unknown')}")
        print(f"🏷️ SQL State: {getattr(e, 'sqlstate', 'Unknown')}")
        
        # Detailed error analysis
        error_msg = str(e).lower()
        if "ssl" in error_msg:
            print("\n🔒 SSL Issue:")
            print("- Check if ca.pem is the correct certificate")
            print("- Verify SSL mode is REQUIRED in Aiven")
        elif "access denied" in error_msg:
            print("\n🚫 Access Issue:")
            print("- Check username and password")
            print("- Verify IP is whitelisted")
        elif "timeout" in error_msg or "connection" in error_msg:
            print("\n🔌 Connection Issue:")
            print("- Check if service is running")
            print("- Verify network connectivity")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_aiven()
    if success:
        print("\n🎉 Aiven connection successful!")
    else:
        print("\n💔 Aiven connection failed!")