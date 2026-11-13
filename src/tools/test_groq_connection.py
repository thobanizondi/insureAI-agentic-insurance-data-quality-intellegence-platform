
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file")

# Initialise Groq client
client = Groq(api_key=api_key)

# Send a test request
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are an AI assistant specialising in insurance data analytics."
        },
        {
            "role": "user",
            "content": "Briefly explain how AI can investigate an insurance claim that exceeds its policy coverage."
        }
    ],
    max_completion_tokens=250
)

print("\nINSUREAI - GROQ API TEST")
print("=" * 50)
print(response.choices[0].message.content)
print("\nGroq API connection successful!")
