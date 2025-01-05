from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from app.utils.tools import get_cake_inventory
from app.utils.function_schemas import function_to_schema

from dotenv import load_dotenv
import os
import json
import logging
from typing import Any

# Configure logging at the top of the file
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables at the start of the application
load_dotenv()

app = FastAPI(title="Bakery Chatbot API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add at the top of the file, outside any function
conversation_history: list[dict] = []


def execute_tool_call(tool_call, tools_map):
    try:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        logger.debug(f"Executing tool call: {name} with args: {args}")
        logger.debug(f"Available tools: {list(tools_map.keys())}")

        if name not in tools_map:
            raise ValueError(f"Tool {name} not found in tools_map")

        # call corresponding function with provided arguments
        result = tools_map[name](**args)
        logger.debug(f"Tool call result (raw): {result}")
        
        # Ensure the result is JSON serializable
        json_result = json.dumps(result)
        logger.debug(f"Tool call result (serialized): {json_result}")
        
        return json_result
    except Exception as e:
        logger.error(f"Error in execute_tool_call: {str(e)}", exc_info=True)
        raise



def run_full_turn(system_message: str, messages: list[dict], tools: list = None) -> dict:
    """
    Run a complete conversation turn with the OpenAI API, handling tool calls
    
    Args:
        system_message (str): The system message to guide the model
        messages (list[dict]): The conversation history
        tools (list, optional): List of tool functions to make available
    
    Returns:
        dict: The assistant's response message
    """

    messages = messages.copy()
    try:
        # Convert python functions into tools and create reverse mapping
        tool_schemas = [function_to_schema(tool) for tool in tools] if tools else None
        tools_map = {tool.__name__: tool for tool in tools} if tools else {}

        while True:
            # Get completion from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[{"role": "system", "content": system_message}] + messages,
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

            # If no tool calls, return the message
            if not message.tool_calls:
                return assistant_message

            # Handle tool calls
            for tool_call in message.tool_calls:
                result = execute_tool_call(tool_call, tools_map)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
                messages.append(tool_message)

    except Exception as e:
        logger.error(f"Error in run_full_turn: {str(e)}", exc_info=True)
        raise



@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(request: Request) -> dict:
    try:
        global conversation_history
        data = await request.json()
        message = data.get('message', '')

        # Check for exit message
        if message.lower() in ['exit', 'quit', 'bye']:
            print("\n=== Conversation History ===")
            for msg in conversation_history:
                print(f"{msg['role'].capitalize()}: {msg['content']}")
            print("==========================\n")
            
            final_history = conversation_history.copy()
            conversation_history = []
            
            return {
                "response": "Goodbye! Conversation history has been cleared.",
                "conversation_history": final_history
            }

        # system_message = """You are a helpful bakery assistant. Provide friendly and 
        # informative responses about bakery products, ingredients, and services."""

        system_message = (
            "You are a friendly customer service agent for Chocolate Therapy Bakery. "
            "Start with: 'Welcome to chocolate therapy, let's cure your cravings with a heavy dose of sweetness'\n"
            "Follow this routine with customers:\n"
            "1. Ask if they want immediate pickup or custom cake order\n"
            "2. For immediate pickup:\n"
            "   - Inform about available cakes\n"
            "3. For custom cake orders, collect in a friendly conversation:\n"
            "   - Occasion\n"
            "   - Cake size (number of people)\n"
            "   - Number of tiers\n"
            "   - Dietary restrictions\n"
            "   - Filling and frosting preferences\n"
            "   - Theme or design preferences\n"
            "   - Color preferences\n"
            "   - Special message or decorations\n"
            "   - Customer name\n"
            "4. Summarize the complete order\n"
            "5. Get final confirmation from customer\n"
        )

        tools = [get_cake_inventory]
        
        conversation_history.append({
            "role": "user", 
            "content": message
        })
        
        assistant_message = run_full_turn(
            system_message, 
            conversation_history,
            tools
        )
        
        conversation_history.append(assistant_message)
        
        return {
            "response": assistant_message["content"],
            "conversation_history": conversation_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 