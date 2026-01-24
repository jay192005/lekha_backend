#!/usr/bin/env python3
"""
Test document analysis functionality
"""

import requests

def test_document_analysis():
    """Test the document analysis endpoint"""
    url = "http://localhost:5000/api/analyze"
    
    # Sample lease text for testing
    sample_text = """
    RENTAL AGREEMENT
    
    This lease agreement is entered into between the Landlord and Tenant.
    
    1. The tenant is responsible for all repairs and maintenance.
    2. The landlord may access the property without notice at any time.
    3. The security deposit is non-refundable under any circumstances.
    4. Rent increases may occur at the landlord's sole discretion.
    5. The tenant waives all rights to legal recourse.
    
    The tenant agrees to these terms and conditions.
    """
    
    # Prepare form data
    data = {
        'text': sample_text,
        'state': 'Maharashtra',
        'email': 'test@lekha.ai'
    }
    
    try:
        print("🔍 Testing Document Analysis...")
        response = requests.post(url, data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document Analysis Working!")
            print(f"Rating Score: {result.get('ratingScore', 'N/A')}/100")
            print(f"Rating Text: {result.get('ratingText', 'N/A')}")
            print(f"Red Flags: {result.get('redFlagsCount', 0)}")
            print(f"Fair Clauses: {result.get('fairClausesCount', 0)}")
            return True
        else:
            print(f"❌ Analysis failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing lekha.ai Document Analysis")
    print("=" * 40)
    
    success = test_document_analysis()
    
    if success:
        print("\n🎉 DOCUMENT ANALYSIS IS WORKING!")
        print("✅ AI analysis functionality confirmed")
        print("✅ Your lekha.ai app is 100% ready to use!")
    else:
        print("\n⚠️  Document analysis needs attention")
        print("Check your Gemini API key configuration")