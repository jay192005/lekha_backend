#!/usr/bin/env python3
"""
Check available Gemini models and test API
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

def check_models():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    api_key = api_key.strip('"\'')
    genai.configure(api_key=api_key)
    
    # Try different model names
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest', 
        'gemini-1.5-pro',
        'gemini-1.5-pro-latest',
        'gemini-pro',
        'gemini-pro-latest',
        'models/gemini-1.5-flash',
        'models/gemini-pro'
    ]
    
    print("Testing different model names:")
    print("=" * 40)
    
    for model_name in model_names:
        try:
            print(f"\n🧪 Testing: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, this is a test.")
            print(f"✅ SUCCESS: {model_name}")
            print(f"Response: {response.text[:50]}...")
            return model_name  # Return the first working model
        except Exception as e:
            print(f"❌ FAILED: {model_name} - {str(e)[:100]}...")
    
    print("\n❌ No working models found!")
    
    # Try to list available models
    try:
        print("\n🔍 Attempting to list available models...")
        models = genai.list_models()
        print("Available models:")
        for model in models:
            if hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    print(f"✅ {model.name}")
            else:
                print(f"? {model.name}")
    except Exception as e:
        print(f"❌ Could not list models: {e}")

if __name__ == "__main__":
    check_models()