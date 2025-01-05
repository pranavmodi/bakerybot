from pydantic import BaseModel
from typing import List, Dict, Callable, Any
from .tools import get_cake_inventory, calculate_custom_cake_price, check_payment_status


class Agent(BaseModel):
    name: str = "Agent"
    model: str = "gpt-4-0125-preview"
    instructions: str = "You are a helpful Agent"
    tools: list = []


class BakeryAgent(Agent):
    name: str = "BakeryBot"
    instructions: str = """You are a friendly customer service agent for Chocolate Therapy Bakery.
    Start with: 'Welcome to chocolate therapy, let's cure your cravings with a heavy dose of sweetness'

    Follow this routine with customers:
    1. Ask if they want immediate pickup or custom cake order
    2. For immediate pickup:
       - Inform about available cakes
    3. For custom cake orders, collect in a friendly conversation:
       - Occasion
       - Cake size (number of people)
       - Number of tiers
       - Dietary restrictions
       - Filling and frosting preferences
       - Theme or design preferences
       - Color preferences
       - Special message or decorations
       - Customer name
    4. Summarize the complete order
    5. Get final confirmation from customer

    Additional Guidelines:
    - Base custom cakes start at $30
    - All prices are in USD
    - Payment must be confirmed before order processing
    - Special dietary requirements may affect pricing
    - Always note allergies and dietary restrictions
    - Recommend alternatives when requested items are unavailable
    """
    
    tools: List[Dict[str, Any]] = [
        {
            "name": "get_cake_inventory",
            "function": get_cake_inventory,
            "description": "Get the current list of available cakes"
        },
        {
            "name": "calculate_custom_cake_price",
            "function": calculate_custom_cake_price,
            "description": "Calculate price for a custom cake based on description"
        },
        {
            "name": "check_payment_status",
            "function": check_payment_status,
            "description": "Check if a payment was successful"
        }
    ]