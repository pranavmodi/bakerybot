from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from dotenv import load_dotenv
import os

# Load environment variables at the start of the application
load_dotenv()

app = FastAPI(title="Bakery Chatbot API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatMessage(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful bakery assistant. Provide friendly and informative responses about bakery products, ingredients, and services."},
            {"role": "user", "content": chat_message.message}
        ])
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 