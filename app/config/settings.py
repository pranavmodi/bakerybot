from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str = "postgresql://user:password@localhost:5432/bakery_chatbot"

    class Config:
        env_file = ".env" 