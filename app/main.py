from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from openai import OpenAI
from app.utils.tools import bakery_agent, Agent
from app.utils.function_schemas import function_to_schema
from app.services.chat_service import ChatService
from app.services.response_service import ResponseService
from app.utils.logging_config import setup_logging
from app.models import Conversation, ConversationManager
from dotenv import load_dotenv
from app.config.settings import INPUT_FORMAT
import os
import json
import argparse
from typing import Any, List, Dict
from datetime import datetime

# Configure logging
logger = setup_logging()

# Load environment variables at the start of the application
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description='Bakery Chatbot API')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    return parser.parse_args()

app = FastAPI(title="Bakery Chatbot API")

# Initialize services
chat_service = ChatService(
    openai_client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    initial_agent=bakery_agent
)
response_service = ResponseService()
conversation_manager = ConversationManager()

@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(request: Request) -> Response:
    try:
        logger.info("\n=== Request received ===")
        
        # Log raw request details
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Parse form data from Twilio
        form_data = await request.form()
        logger.info(f"Form data: {dict(form_data)}")
        
        # Extract phone number from the From field (format: whatsapp:+1234567890)
        phone_number = form_data.get("From", "").replace("whatsapp:", "")
        if not phone_number:
            error_msg = "No phone number provided in request"
            logger.error(error_msg)
            return response_service.create_error_response(error_msg)
        
        # Extract message from the Body field
        message = form_data.get("Body")
        if not message:
            error_msg = "No message found in request"
            logger.error(error_msg)
            return response_service.create_error_response(error_msg)

        logger.info(f"Phone number: {phone_number}")
        logger.info(f"Message: {message}")
        
        # Get or create conversation for this phone number
        conversation = conversation_manager.get_conversation(phone_number)
        
        # Process the message with conversation context
        response_text = await chat_service.process_message(message, conversation)
        
        # Cleanup old conversations
        conversation_manager.cleanup_old_conversations()
        
        # Return response based on input format
        return response_service.create_response(response_text)
            
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}", exc_info=True)
        return response_service.create_error_response(f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    args = parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)