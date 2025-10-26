"""
Quick test to verify OpenAI API key works
"""
import os
from dotenv import load_dotenv

# Load from backend/.env
load_dotenv('backend/.env')

api_key = os.getenv('OPENAI_API_KEY')

print(f"API Key found: {bool(api_key)}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

# Try to use it
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print("\n✓ OpenAI client created successfully")
    
    # Make a simple test call
    print("\nTesting API with a simple call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'API works!' in 2 words"}
        ],
        max_tokens=10
    )
    
    print(f"✓ API Response: {response.choices[0].message.content}")
    print("\n✅ OpenAI API is working correctly!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
