from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from openai import OpenAI
from app.utils.tools import bakery_agent, Agent
from app.utils.function_schemas import function_to_schema
from app.services.chat_service import ChatService
from app.services.response_service import ResponseService
from app.utils.logging_config import setup_logging
from dotenv import load_dotenv
from app.config.settings import INPUT_FORMAT
import os
import json
from typing import Any

# Configure logging
logger = setup_logging()

# Load environment variables at the start of the application
load_dotenv()

app = FastAPI(title="Bakery Chatbot API")

# Initialize services
chat_service = ChatService(
    openai_client=OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
    initial_agent=bakery_agent
)
response_service = ResponseService()

@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(request: Request) -> Response:
    try:
        logger.info("\n=== Request received ===")
        
        # Log raw request details
        logger.info(f"Headers: {dict(request.headers)}")
        body = await request.body()
        logger.info(f"Raw body: {body}")
        
        # Extract message based on configured input format
        message = await response_service.extract_message(request)
        
        if not message:
            error_msg = "No message found in request"
            logger.error(error_msg)
            return response_service.create_error_response(error_msg)

        logger.info(f"Extracted message: {message}")
        logger.info("==============================\n")
        
        # Process the message
        response_text = await chat_service.process_message(message)
        
        # Return response based on input format
        return response_service.create_response(response_text)
            
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}", exc_info=True)
        return response_service.create_error_response(f"Internal server error: {str(e)}")