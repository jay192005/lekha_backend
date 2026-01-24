#!/usr/bin/env python3
"""
Test Gemini API directly to diagnose the issue
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

def test_gemini_api():
    """Test the Gemini API directly"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key loaded: {api_key[:10]}...{api_key[-10:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple model
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Simple test prompt
        test_prompt = """
        Analyze this simple rental clause and respond with JSON:
        "The tenant must pay rent on the 1st of each month."
        
        Respond with this exact JSON format:
        {
            "ratingScore": 85,
            "ratingText": "SAFE",
            "shortSummary": "Standard rent payment clause",
            "aiSummary": "This is a standard rental payment requirement.",
            "redFlags": [],
            "fairClauses": [{"title": "Standard Payment Terms", "recommendation": "This is a fair clause"}],
            "recommendations": ["Review payment methods with landlord"]
        }
        """
        
        print("🔍 Testing Gemini API...")
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        response = model.generate_content(test_prompt, generation_config=generation_config)
        
        print("✅ API Response received!")
        print(f"Response text: {response.text[:200]}...")
        
        # Try to parse JSON
        try:
            # Clean the response text
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
                
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            print("✅ JSON parsing successful!")
            print(f"Rating Score: {result.get('ratingScore')}")
            print(f"Rating Text: {result.get('ratingText')}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_api_key_validity():
    """Test if the API key is valid"""
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    if len(api_key) < 30:
        print("❌ API key seems too short")
        return False
    
    if not api_key.startswith('AIza'):
        print("❌ API key doesn't have correct format")
        return False
    
    print("✅ API key format looks correct")
    return True

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration")
    print("=" * 40)
    
    print("\n🔑 Testing API Key:")
    key_valid = test_api_key_validity()
    
    if key_valid:
        print("\n🤖 Testing Gemini API:")
        api_working = test_gemini_api()
        
        if api_working:
            print("\n🎉 GEMINI API IS WORKING!")
            print("✅ The issue might be elsewhere in the code")
        else:
            print("\n❌ GEMINI API FAILED!")
            print("🔧 Possible solutions:")
            print("1. Check if your API key is valid and active")
            print("2. Verify you have Gemini API access enabled")
            print("3. Check your internet connection")
            print("4. Try generating a new API key")
    else:
        print("\n❌ API KEY ISSUE!")
        print("🔧 Please check your .env file and API key")