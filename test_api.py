#!/usr/bin/env python3
"""
Test script to check the API functionality
"""

import requests
import json

def test_analyze_api():
    """Test the document analysis API"""
    
    print("🧪 Testing Document Analysis API...")
    print("=" * 50)
    
    # Test data
    test_text = """
    RENTAL AGREEMENT
    
    This agreement is between the landlord and tenant.
    
    1. The tenant must pay rent on the 1st of each month.
    2. No pets are allowed on the property.
    3. The tenant is responsible for all repairs and maintenance.
    4. The landlord can access the property without notice.
    5. The security deposit is non-refundable.
    6. Late fees of 10% will be charged for overdue rent.
    """
    
    # Prepare form data
    data = {
        'text': test_text,
        'state': 'Maharashtra',
        'email': 'test@example.com'
    }
    
    try:
        print("📤 Sending request to API...")
        response = requests.post('http://localhost:5000/api/analyze', data=data)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response successful!")
            print(f"🎯 Rating Score: {result.get('ratingScore', 'N/A')}")
            print(f"⚠️ Rating Text: {result.get('ratingText', 'N/A')}")
            print(f"📝 Summary: {result.get('shortSummary', 'N/A')}")
            print(f"🚩 Red Flags Count: {result.get('redFlagsCount', 0)}")
            print(f"✅ Fair Clauses Count: {result.get('fairClausesCount', 0)}")
            
            if 'redFlags' in result and result['redFlags']:
                print("\n🚩 Red Flags Found:")
                for i, flag in enumerate(result['redFlags'][:3], 1):  # Show first 3
                    print(f"  {i}. {flag.get('title', 'Unknown')}")
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_api():
    """Test the health check API"""
    
    print("\n🏥 Testing Health Check API...")
    print("=" * 30)
    
    try:
        response = requests.get('http://localhost:5000/api/health')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Status: {result.get('status', 'unknown')}")
            print(f"🗄️ Database: {result.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 API Testing Suite")
    print("=" * 50)
    
    # Test health first
    health_ok = test_health_api()
    
    if health_ok:
        # Test analysis API
        analyze_ok = test_analyze_api()
        
        if analyze_ok:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️ Analysis API test failed")
    else:
        print("\n❌ Health check failed - skipping other tests")
    
    print("\n" + "=" * 50)
    print("✨ Testing completed!")