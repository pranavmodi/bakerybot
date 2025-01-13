from typing import Dict, List, Any, Tuple
from openai import OpenAI
from app.utils.tools import Agent
from app.utils.function_schemas import function_to_schema
from app.models import Conversation
import json
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, openai_client: OpenAI, initial_agent: Agent):
        self.client = openai_client
        self.initial_agent = initial_agent
        self.current_agent = initial_agent

    def _print_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Print messages in a readable format for debugging."""
        print("\n=== Messages being sent to OpenAI ===")
        for msg in messages:
            print(f"Role: {msg['role']}")
            print(f"Content: {msg['content']}")
            if 'tool_calls' in msg:
                print(f"Tool calls: {msg['tool_calls']}")
            print("---")
        print("===================================\n")

    def _execute_tool_call(self, tool_call: Any, tools: Dict[str, Any]) -> Any:
        """Execute a tool call and return the result."""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        print(f"{self.current_agent.name}:", f"{name}({args})")
        return tools[name](**args)

    async def _run_full_turn(self, messages: List[Dict[str, Any]], conversation: Conversation) -> Tuple[Dict[str, Any], Agent]:
        """Run a complete conversation turn with OpenAI API."""
        messages = messages.copy()
        try:
            # Create tool schemas and mapping
            tool_schemas = [function_to_schema(tool) for tool in self.current_agent.tools]
            tools_map = {tool.__name__: tool for tool in self.current_agent.tools}

            while True:
                # Get completion from OpenAI
                print(f"Current agent: {self.current_agent.name}")
                full_messages = [{"role": "system", "content": self.current_agent.instructions}] + messages
                self._print_messages(full_messages)
                
                response = self.client.chat.completions.create(
                    model=self.current_agent.model,
                    messages=full_messages,
                    tools=tool_schemas,
                )
                message = response.choices[0].message

                # Prepare assistant message
                assistant_message = {
                    "role": "assistant",
                    "content": message.content or ""
                }
                
                # Add tool_calls if they exist
                if message.tool_calls:
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        } 
                        for tc in message.tool_calls
                    ]
                
                messages.append(assistant_message)

                if not message.tool_calls:
                    return assistant_message, self.current_agent

                # Handle tool calls
                for tool_call in message.tool_calls:
                    result = self._execute_tool_call(tool_call, tools_map)
                    
                    if isinstance(result, Agent):
                        self.current_agent = result
                        result = f"Transferred to {self.current_agent.name}. Adopt persona immediately."
                        tool_schemas = [function_to_schema(tool) for tool in self.current_agent.tools]
                        tools_map = {tool.__name__: tool for tool in self.current_agent.tools}
                    
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    }
                    messages.append(tool_message)

        except Exception as e:
            logger.error(f"Error in run_full_turn: {str(e)}")
            raise

    async def process_message(self, message: str, conversation: Conversation) -> str:
        """Process a user message and return the response."""
        if message.lower() in ['exit', 'quit', 'bye']:
            conversation.history = []
            self.current_agent = self.initial_agent
            return "Goodbye! Conversation history has been cleared."

        # Add user message to conversation history
        conversation.history.append({
            "role": "user",
            "content": message
        })

        # Run the full turn with tools and agent switching
        assistant_message, _ = await self._run_full_turn(conversation.history, conversation)
        
        # Add assistant response to conversation history
        conversation.history.append(assistant_message)
        
        return assistant_message["content"] 