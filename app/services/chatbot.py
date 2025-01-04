from openai import OpenAI
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str

    class Config:
        env_file = ".env"

class ChatbotService:
    def __init__(self):
        self.settings = Settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def generate_response(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful bakery assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}" 