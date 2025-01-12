from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from openai import OpenAI
from app.utils.tools import bakery_agent, Agent
from app.utils.function_schemas import function_to_schema
from dotenv import load_dotenv
from app.config.settings import INPUT_FORMAT
import os
import json
from typing import Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables at the start of the application
load_dotenv()

app = FastAPI(title="Bakery Chatbot API")

# Initialize OpenAI client and BakeryAgent
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add at the top of the file, outside any function
conversation_history: list[dict] = []
current_agent = bakery_agent  # Initialize with bakery_agent

def print_messages(messages: list[dict]) -> None:
    """Print messages in a readable format for debugging."""
    print("\n=== Messages being sent to OpenAI ===")
    for msg in messages:
        print(f"Role: {msg['role']}")
        print(f"Content: {msg['content']}")
        if 'tool_calls' in msg:
            print(f"Tool calls: {msg['tool_calls']}")
        print("---")
    print("===================================\n")

def execute_tool_call(tool_call, tools, agent_name):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"{agent_name}:", f"{name}({args})")

    return tools[name](**args)  # call corresponding function with provided arguments

def run_full_turn(agent: Agent, messages: list[dict]) -> tuple[dict, Agent]:
    """
    Run a complete conversation turn with the OpenAI API, handling tool calls and agent transfers
    
    Args:
        agent (Agent): The current agent containing instructions and tools
        messages (list[dict]): The conversation history
    
    Returns:
        tuple[dict, Agent]: The assistant's response message and the current agent (which may have changed)
    """

    messages = messages.copy()
    current_agent = agent
    try:
        # Create tool schemas and mapping
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools_map = {tool.__name__: tool for tool in current_agent.tools}

        while True:
            # Get completion from OpenAI
            print(f"Current agent: {current_agent.name}")
            full_messages = [{"role": "system", "content": current_agent.instructions}] + messages
            print_messages(full_messages)
            response = client.chat.completions.create(
                model=current_agent.model,
                messages=full_messages,
                tools=tool_schemas,
            )
            message = response.choices[0].message

            # If there's content, prepare to return it
            assistant_message = {
                "role": "assistant",
                "content": message.content or ""
            }
            
            # Only add tool_calls if they exist
            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } 
                    for tc in message.tool_calls
                ]
            
            # Add assistant message to history before processing tool calls
            messages.append(assistant_message)

            # If no tool calls, return the message and current agent
            if not message.tool_calls:
                return assistant_message, current_agent

            # Handle tool calls
            for tool_call in message.tool_calls:
                result = execute_tool_call(tool_call, tools_map, current_agent.name)
                
                # Check if result is an Agent (indicating agent transfer)
                if isinstance(result, Agent):
                    current_agent = result
                    result = f"Transferred to {current_agent.name}. Adopt persona immediately."
                    # Update tool schemas and mapping for new agent
                    tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
                    tools_map = {tool.__name__: tool for tool in current_agent.tools}
                
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
                messages.append(tool_message)

    except Exception as e:
        print(f"Error in run_full_turn: {str(e)}")
        raise

def create_twilio_response(message: str) -> str:
    """Create a TwiML response for Twilio."""
    # Escape any XML special characters in the message
    message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""

@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(request: Request) -> Response:
    try:
        global conversation_history
        global current_agent
        
        logger.info("\n=== Request received ===")
        
        # Log raw request details
        logger.info(f"Headers: {dict(request.headers)}")
        body = await request.body()
        logger.info(f"Raw body: {body}")
        
        # Extract message based on configured input format
        if INPUT_FORMAT == "form":
            try:
                form_data = await request.form()
                message = form_data.get('Body', '')
                logger.info(f"Form data received: {dict(form_data)}")
            except Exception as e:
                logger.error(f"Error parsing form data: {str(e)}")
                return Response(
                    content=create_twilio_response(f"Error processing request: {str(e)}"),
                    media_type="text/xml",
                    status_code=400
                )
        else:  # json format
            try:
                data = await request.json()
                logger.info(f"JSON data received: {json.dumps(data, indent=2)}")
                message = data.get('message', '')
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")

        if not message:
            error_msg = "No message found in request"
            logger.error(error_msg)
            if INPUT_FORMAT == "form":
                return Response(
                    content=create_twilio_response(error_msg),
                    media_type="text/xml",
                    status_code=400
                )
            raise HTTPException(status_code=400, detail=error_msg)

        logger.info(f"Extracted message: {message}")
        logger.info("==============================\n")
        
        # Check for exit message
        if message.lower() in ['exit', 'quit', 'bye']:
            final_history = conversation_history.copy()
            conversation_history = []
            current_agent = bakery_agent  # Reset to bakery agent
            response_text = "Goodbye! Conversation history has been cleared."
        else:
            conversation_history.append({
                "role": "user", 
                "content": message
            })
            
            assistant_message, current_agent = run_full_turn(
                current_agent,
                conversation_history
            )
            
            conversation_history.append(assistant_message)
            response_text = assistant_message["content"]

        # Return response based on input format
        if INPUT_FORMAT == "form":
            twiml_response = create_twilio_response(response_text)
            return Response(
                content=twiml_response,
                media_type="text/xml",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            return JSONResponse(content={
                "response": response_text,
                "conversation_history": conversation_history,
                "current_agent": current_agent.name
            })
            
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}", exc_info=True)
        error_message = f"Internal server error: {str(e)}"
        if INPUT_FORMAT == "form":
            twiml_response = create_twilio_response(error_message)
            return Response(
                content=twiml_response,
                media_type="text/xml",
                status_code=500,
                headers={"Cache-Control": "no-cache"}
            )
        raise HTTPException(status_code=500, detail=error_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=50000)