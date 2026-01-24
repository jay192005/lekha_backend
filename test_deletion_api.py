#!/usr/bin/env python3
"""
Test script to check the deletion API functionality
"""

import requests
import json

def test_delete_data_api():
    """Test the delete data API"""
    
    print("🗑️ Testing Delete Data API...")
    print("=" * 40)
    
    # Test 1: Try to delete from analysis_history (should work)
    test_data = {
        "table": "analysis_history",
        "operation": "truncate"
    }
    
    try:
        print("📤 Testing TRUNCATE operation on analysis_history...")
        response = requests.post(
            'http://localhost:5000/api/delete-data',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ TRUNCATE operation successful!")
            print(f"📋 Message: {result.get('message', 'N/A')}")
            print(f"🎯 Affected Rows: {result.get('affected_rows', 'N/A')}")
        else:
            print(f"❌ TRUNCATE failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ TRUNCATE test error: {e}")
    
    # Test 2: Try to delete specific user (should work if user exists)
    test_data2 = {
        "table": "users",
        "operation": "delete",
        "conditions": {
            "email": "nonexistent@example.com"
        }
    }
    
    try:
        print("\n📤 Testing DELETE operation on users...")
        response = requests.post(
            'http://localhost:5000/api/delete-data',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data2)
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE operation successful!")
            print(f"📋 Message: {result.get('message', 'N/A')}")
            print(f"🎯 Affected Rows: {result.get('affected_rows', 'N/A')}")
        else:
            print(f"❌ DELETE failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ DELETE test error: {e}")
    
    # Test 3: Try invalid table (should fail)
    test_data3 = {
        "table": "invalid_table",
        "operation": "truncate"
    }
    
    try:
        print("\n📤 Testing invalid table (should fail)...")
        response = requests.post(
            'http://localhost:5000/api/delete-data',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data3)
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Security check working - invalid table rejected!")
            result = response.json()
            print(f"📋 Error: {result.get('error', 'N/A')}")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Invalid table test error: {e}")

def test_clear_history_api():
    """Test the clear history API"""
    
    print("\n🧹 Testing Clear History API...")
    print("=" * 35)
    
    test_data = {
        "email": "test@example.com"
    }
    
    try:
        print("📤 Testing clear history for specific user...")
        response = requests.post(
            'http://localhost:5000/api/clear-history',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Clear history successful!")
            print(f"📋 Message: {result.get('message', 'N/A')}")
            print(f"🎯 Affected Rows: {result.get('affected_rows', 'N/A')}")
        else:
            print(f"❌ Clear history failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Clear history test error: {e}")

if __name__ == "__main__":
    print("🚀 Deletion API Testing Suite")
    print("=" * 50)
    
    # Test deletion APIs
    test_delete_data_api()
    test_clear_history_api()
    
    print("\n" + "=" * 50)
    print("✨ Deletion API testing completed!")