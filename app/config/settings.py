from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INPUT_FORMAT = os.getenv("INPUT_FORMAT", "json").lower()  # Can be 'json' or 'form'

# Validate input format
if INPUT_FORMAT not in ["json", "form"]:
    raise ValueError("INPUT_FORMAT must be either 'json' or 'form'")

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "postgresql://user:password@localhost:5432/bakery_chatbot"

    class Config:
        env_file = ".env" 