from typing import List, Dict, Callable, Any
from pydantic import BaseModel
import random

class Agent(BaseModel):
    name: str = "Agent"
    model: str = "gpt-4-0125-preview"
    instructions: str = "You are a helpful Agent"
    tools: list = []

def get_cake_inventory() -> List[Dict[str, str]]:
    """
    Get the current inventory of available cakes.
    
    Returns:
        List[Dict[str, str]]: List of cakes with their details
    """
    return [
        {
            "name": "Chocolate Therapy",
            "description": "Triple chocolate cake with ganache filling",
            "price": "$45.00",
            "availability": "in stock"
        },
        {
            "name": "Red Velvet Dream",
            "description": "Classic red velvet with cream cheese frosting",
            "price": "$40.00",
            "availability": "in stock"
        },
        {
            "name": "Vanilla Bean Bliss",
            "description": "Madagascar vanilla bean cake with buttercream",
            "price": "$35.00",
            "availability": "limited"
        }
    ]

def calculate_custom_cake_price(description: str) -> float:
    """
    Calculate the price of a custom cake based on its description.
    Base price is $30, with additional costs for special features.
    
    Args:
        description (str): Description of the custom cake
        
    Returns:
        float: Calculated price of the cake
    """
    base_price = 30.0
    description = description.lower()
    
    if "tiered" in description or "tier" in description:
        base_price += 20.0 * description.count("tier")
    if "fondant" in description:
        base_price += 15.0
    if "chocolate" in description:
        base_price += 5.0
    if "fresh fruit" in description or "berries" in description:
        base_price += 8.0
    if "custom design" in description or "decorated" in description:
        base_price += 10.0
    if "gluten free" in description or "gluten-free" in description:
        base_price += 5.0
        
    return round(base_price, 2)

def check_payment_status() -> bool:
    """
    Simulate a payment status check that returns success 70% of the time.
    """
    return random.random() < 0.7

def execute_refund() -> bool:
    """
    Execute a refund transaction for a customer order.
    """
    return True

def transfer_to_custom_order_agent() -> Agent:
    """Transfer the conversation to the custom order specialist agent."""
    return custom_order_agent

def transfer_to_bakery_agent() -> Agent:
    """Transfer the conversation to the general bakery agent."""
    return bakery_agent

def transfer_to_refund_agent() -> Agent:
    """Transfer the conversation to the refund specialist agent."""
    return refund_agent

# Define agent instances
bakery_agent = Agent(
    name="BakeryBot",
    instructions="""You are a friendly customer service agent for Chocolate Therapy Bakery.
    Start with: 'Welcome to chocolate therapy, let's cure your cravings with a heavy dose of sweetness'

    Follow this routine with customers:
    1. Ask if they want immediate pickup or custom cake order
    2. For immediate pickup:
       - Inform about available cakes using get_cake_inventory
       - Process payment and confirm order
    3. For custom cake orders:
       - Hand over to custom_order_agent with message: "Transferring you to our custom order specialist"
    4. If customer mentions refund or cancellation:
       - Hand over to refund_agent with message: "Let me connect you with our refund specialist"

    Additional Guidelines:
    - All prices are in USD
    - Payment must be confirmed before order processing
    - Be friendly but efficient
    - If unsure about any request, clarify before proceeding
    """,
    model="gpt-4-0125-preview",
    tools=[get_cake_inventory, calculate_custom_cake_price, check_payment_status, 
           transfer_to_custom_order_agent, transfer_to_refund_agent]
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="""You are a refund specialist for Chocolate Therapy Bakery.
    Start with: "I understand you'd like to discuss a refund. I'm here to help."

    Follow this routine:
    1. Get order ID and reason for refund
    2. Check if refund is eligible based on:
       - Time since order
       - Order status
       - Previous refund history
    3. Process refund if eligible using execute_refund
    4. If refund is not possible, explain why clearly
    5. If customer wants to place a new order:
       - Hand over to bakery_agent with message: "Let me connect you with our order specialist"

    Guidelines:
    - Be empathetic but follow policy
    - Document all refund reasons
    - Refunds only possible within 24 hours of order for non-custom items
    - Custom orders are non-refundable once production begins
    """,
    model="gpt-4-0125-preview",
    tools=[execute_refund, transfer_to_bakery_agent]
)

custom_order_agent = Agent(
    name="Order Agent",
    instructions="""You are a custom order specialist for Chocolate Therapy Bakery.
    Start with: "I'm excited to help create your perfect custom cake!"

    Follow this routine for custom orders:
    1. Collect requirements in a friendly conversation:
       - Occasion
       - Cake size (number of people)
       - Number of tiers
       - Dietary restrictions
       - Filling and frosting preferences
       - Theme or design preferences
       - Color preferences
       - Special message or decorations
       - Customer name
    2. Calculate price using calculate_custom_cake_price
    3. Summarize order details
    4. Get final confirmation
    5. Process payment using check_payment_status
    
    If at any point:
    - Customer mentions refund: Hand over to refund_agent
    - Customer wants regular cake: Hand over to bakery_agent
    
    Guidelines:
    - Base custom cakes start at $30
    - Special dietary requirements affect pricing
    - Always note allergies
    - 72 hours minimum notice required
    - Payment required upfront
    """,
    model="gpt-4-0125-preview",
    tools=[calculate_custom_cake_price, check_payment_status, transfer_to_bakery_agent, transfer_to_refund_agent]
)