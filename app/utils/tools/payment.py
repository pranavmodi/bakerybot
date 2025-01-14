import random

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