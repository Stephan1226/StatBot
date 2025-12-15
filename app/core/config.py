import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    CORS_ORIGINS: list = ["http://localhost:5173"]

settings = Settings()