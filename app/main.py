from fastapi import FastAPI, HTTPException, Request
from openai import OpenAI
from app.utils.tools import bakery_agent, Agent
from app.utils.function_schemas import function_to_schema
from dotenv import load_dotenv
import os
import json
from typing import Any

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

@app.get("/")
async def root():
    return {"message": "Welcome to the Bakery Chatbot API"}

@app.post("/chat")
async def chat(request: Request) -> dict:
    try:
        global conversation_history
        global current_agent
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
            current_agent = bakery_agent  # Reset to bakery agent
            
            return {
                "response": "Goodbye! Conversation history has been cleared.",
                "conversation_history": final_history
            }

        conversation_history.append({
            "role": "user", 
            "content": message
        })
        
        assistant_message, current_agent = run_full_turn(
            current_agent,
            conversation_history
        )
        
        conversation_history.append(assistant_message)
        
        return {
            "response": assistant_message["content"],
            "conversation_history": conversation_history,
            "current_agent": current_agent.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 