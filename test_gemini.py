#!/usr/bin/env python3
"""
Test script to verify Gemini AI API connection
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection and model"""
    
    print("🤖 Testing Gemini AI API...")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    print(f"🔑 API Key found: {api_key[:20]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key.strip('"\''))
        
        # List available models
        print("\n📋 Available models:")
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  ✅ {model.name}")
        
        # Test with different model names
        model_names_to_try = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'models/gemini-pro'
        ]
        
        for model_name in model_names_to_try:
            try:
                print(f"\n🧪 Testing model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Simple test
                response = model.generate_content("Hello, respond with 'API working'")
                print(f"✅ {model_name} works! Response: {response.text}")
                return True
                
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
                continue
        
        print("\n❌ No working models found")
        return False
        
    except Exception as e:
        print(f"\n❌ Gemini API Error: {e}")
        return False

def test_ai_module():
    """Test our AI module functions"""
    
    print("\n🔬 Testing AI Module Functions...")
    print("=" * 50)
    
    try:
        import ai
        
        # Test rule-based analysis
        test_text = "The tenant is responsible for all repairs and waive your rights to legal action."
        
        print("🔍 Testing rule-based analysis...")
        preliminary = ai.analyze_text_with_rules(test_text)
        print(f"✅ Rule-based analysis works: {preliminary}")
        
        # Test Gemini analysis
        print("\n🤖 Testing Gemini analysis...")
        result = ai.analyze_with_gemini(test_text, preliminary, "Maharashtra")
        
        if "error" in result:
            print(f"❌ Gemini analysis failed: {result['error']}")
            return False
        else:
            print(f"✅ Gemini analysis works!")
            print(f"📊 Rating: {result.get('ratingScore', 'N/A')}")
            print(f"📝 Summary: {result.get('shortSummary', 'N/A')}")
            return True
            
    except Exception as e:
        print(f"❌ AI module test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Gemini AI Test Suite")
    print("=" * 50)
    
    # Test API connection
    api_works = test_gemini_api()
    
    if api_works:
        # Test AI module
        ai_works = test_ai_module()
        
        if ai_works:
            print("\n🎉 All tests passed! AI analysis should work.")
        else:
            print("\n⚠️ API works but AI module has issues.")
    else:
        print("\n❌ API connection failed. Check your API key.")
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")