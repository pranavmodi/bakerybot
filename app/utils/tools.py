from typing import List, Dict
import random

def get_cake_inventory() -> List[Dict[str, str]]:
    """
    Get the current inventory of available cakes.
    
    Returns:
        List[Dict[str, str]]: List of cakes with their details
    """
    # Mock inventory - in a real application, this would query a database
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
    
    # Additional costs for special features
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
    
    Returns:
        bool: True if payment successful (70% probability), False otherwise
    """
    return random.random() < 0.7


    