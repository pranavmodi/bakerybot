from typing import Dict, Union, Optional
from datetime import datetime
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models.database import Order, OrderStatus

def create_order(customer_id: int, order_type: str, total_amount: float, pickup_time: Union[datetime, str, None] = None) -> Dict[str, Union[int, str]]:
    """
    Create a new order in the database.
    
    Args:
        customer_id: The ID of the customer placing the order
        order_type: Type of order ('immediate' or 'custom')
        total_amount: Total amount of the order
        pickup_time: When the order should be picked up (optional). Can be datetime object, ISO format string, or None
        
    Returns:
        Dict containing order details:
        - order_id: The ID of the created order
        - status: Order status
        - message: Status message
    """
    db = next(get_db())
    try:
        # Handle pickup_time
        if pickup_time is None or pickup_time == "":
            pickup_time = datetime.utcnow()
        elif isinstance(pickup_time, str):
            try:
                pickup_time = datetime.fromisoformat(pickup_time.replace('Z', '+00:00'))
            except ValueError:
                pickup_time = datetime.utcnow()
            
        order = Order(
            customer_id=customer_id,
            type=order_type,
            total_amount=total_amount,
            pickup_time=pickup_time,
            status=OrderStatus.PENDING,
            payment_status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return {
            'order_id': order.id,
            'status': order.status.value,
            'message': 'Order created successfully'
        }
    except Exception as e:
        db.rollback()
        return {
            'order_id': None,
            'status': 'failed',
            'message': f'Failed to create order: {str(e)}'
        }
    finally:
        db.close()

def check_payment_status(order_id: int, db: Optional[Session] = None) -> Dict[str, Union[str, float, datetime]]:
    """Check the payment status of an order"""
    if db is None:
        with SessionLocal() as db:
            return _check_payment_status(order_id, db)
    return _check_payment_status(order_id, db)

def _check_payment_status(order_id: int, db: Session) -> Dict[str, Union[str, float, datetime]]:
    """Internal function to handle payment status check logic"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}
    
    return {
        "order_id": order.id,
        "status": order.payment_status,
        "amount": order.total_amount,
        "timestamp": order.created_at
    }

def execute_refund(order_id: int) -> Dict[str, Union[bool, str, datetime]]:
    """
    Execute a refund transaction for a customer order.
    
    Args:
        order_id: The ID of the order to refund
        
    Returns:
        Dict containing refund status:
        - success: Whether the refund was successful
        - refund_id: Unique refund transaction ID
        - timestamp: When the refund was processed
        - message: Status message
    """
    # Simulate a successful refund 95% of the time
    success = random.random() < 0.95
    
    return {
        'success': success,
        'refund_id': f"ref_{order_id}_{hex(random.getrandbits(24))[2:]}" if success else None,
        'timestamp': datetime.utcnow(),
        'message': 'Refund processed successfully' if success else 'Refund failed'
    } 

def update_payment_status(order_id: int, status: str, db: Optional[Session] = None) -> Dict[str, Union[bool, str]]:
    """Update the payment status of an order"""
    if db is None:
        with SessionLocal() as db:
            return _update_payment_status(order_id, status, db)
    return _update_payment_status(order_id, status, db)

def _update_payment_status(order_id: int, status: str, db: Session) -> Dict[str, Union[bool, str]]:
    """Internal function to handle payment status update logic"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"success": False, "error": "Order not found"}
    
    order.payment_status = status
    db.commit()
    return {"success": True, "status": status}

def execute_payment(order_id: int, amount: float) -> Dict[str, Union[bool, str, datetime]]:
    """
    Execute a payment transaction for a customer order.
    
    Args:
        order_id: The ID of the order to process payment for
        amount: The amount to charge
        
    Returns:
        Dict containing payment status:
        - success: Whether the payment was successful (70% chance)
        - payment_id: Unique payment transaction ID
        - timestamp: When the payment was processed
        - message: Status message
    """
    # Simulate a successful payment 70% of the time
    success = random.random() < 0.70
    
    return {
        'success': success,
        'payment_id': f"pay_{order_id}_{hex(random.getrandbits(24))[2:]}" if success else None,
        'timestamp': datetime.utcnow(),
        'message': 'Payment processed successfully' if success else 'Payment failed'
    } 