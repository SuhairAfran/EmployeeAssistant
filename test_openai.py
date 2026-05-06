import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def test_connection():
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}]
            },
            timeout=10.0
        )
        print("Status code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Exception:", str(e))

test_connection()
