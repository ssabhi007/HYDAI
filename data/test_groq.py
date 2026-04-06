import httpx
import os
from dotenv import load_dotenv

load_dotenv()

r = httpx.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
    json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Say: Groq connected successfully"}]
    }
)

print(r.json()["choices"][0]["message"]["content"])