import ai

# Test the AI module
test_text = "Test document with no pets clause"
preliminary = ai.analyze_text_with_rules(test_text)
result = ai.analyze_with_gemini(test_text, preliminary, 'Maharashtra')

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print("Success! AI analysis working.")
    print(f"Rating: {result.get('ratingScore', 'N/A')}")