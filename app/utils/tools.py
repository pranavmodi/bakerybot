from typing import List, Dict

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