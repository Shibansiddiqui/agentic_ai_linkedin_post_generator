import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
GEMINI_MODEL = os.getenv("LLM_MODEL") or "gemini-2.5-flash"
GROQ_MODEL = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"

# API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Email configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")


def get_missing_api_keys():
    required = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "GROQ_API_KEY": GROQ_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
    }

    return [
        key for key, value in required.items()
        if not value
    ]