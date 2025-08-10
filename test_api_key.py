"""
Test Groq API connection
"""
import os
import aiohttp
import asyncio
from app.core.settings import settings

async def test_groq_api():
    """Test basic Groq API connection"""
    
    print("🔧 Testing Groq API Connection")
    print("=" * 40)
    
    print(f"API Key from settings: {settings.GROQ_API_KEY[:20]}...")
    print(f"API Key from env: {os.getenv('GROQ_API_KEY', 'Not found')[:20]}...")
    
    # Test with a simple request
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": "Hello, respond with just 'Hi'"}
        ],
        "max_tokens": 10
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, 
                json=payload
            ) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Success! Response: {result['choices'][0]['message']['content']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_groq_api())
