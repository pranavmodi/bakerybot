from typing import Dict, Any, List

def get_faq() -> List[Dict[str, str]]:
    """
    Get the list of frequently asked questions and their answers from faq.txt.
    
    Returns:
        List[Dict[str, str]]: List of FAQ items with questions and answers
    """
    faqs = []
    try:
        with open('app/faq.txt', 'r') as file:
            current_question = None
            current_answer = None
            
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('Q:'):
                    if current_question and current_answer:
                        faqs.append({
                            "question": current_question,
                            "answer": current_answer
                        })
                    current_question = line[2:].strip()
                    current_answer = None
                elif line.startswith('A:'):
                    current_answer = line[2:].strip()
            
            if current_question and current_answer:
                faqs.append({
                    "question": current_question,
                    "answer": current_answer
                })
                
        return faqs
    except FileNotFoundError:
        return [
            {
                "question": "What are your opening hours?",
                "answer": "We are open Monday to Friday from 7 AM to 7 PM, and weekends from 8 AM to 6 PM."
            },
            {
                "question": "Do you offer gluten-free options?",
                "answer": "Yes, we have a variety of gluten-free breads and pastries available daily."
            },
            {
                "question": "Can I place custom cake orders?",
                "answer": "Yes, custom cake orders require 48 hours advance notice. Please contact us directly for special requests."
            }
        ]

def update_customer_name(customer_id: int, name: str) -> bool:
    """
    Update a customer's name in the database.
    
    Args:
        customer_id (int): The ID of the customer to update
        name (str): The new name for the customer
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    from app.database import get_db
    from app.services.db_service import DatabaseService
    
    try:
        db = next(get_db())
        db_service = DatabaseService(db)
        customer = db_service.update_customer_name(customer_id, name)
        return customer is not None
    except Exception as e:
        print(f"Error updating customer name: {str(e)}")
        return False

def get_customer_by_phone(phone_number: str) -> Dict[str, Any]:
    """
    Get customer details by phone number.
    
    Args:
        phone_number (str): The phone number to look up
        
    Returns:
        Dict[str, Any]: Customer details including name if found, empty dict if not found
    """
    from app.database import get_db
    from app.services.db_service import DatabaseService
    
    try:
        db = next(get_db())
        db_service = DatabaseService(db)
        customer = db_service.get_customer_by_phone(phone_number)
        if customer:
            return {
                "id": customer.id,
                "name": customer.name,
                "phone_number": customer.phone_number,
                "preferences": customer.preferences
            }
        return {}
    except Exception as e:
        print(f"Error getting customer: {str(e)}")
        return {} 