from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models.database import Customer, Order, OrderDetail, ChatHistory

def get_all_customers(db: Session) -> List[Customer]:
    """Get all customers from the database."""
    return db.query(Customer).all()

def get_customer_order_counts(db: Session) -> List[Tuple[str, int]]:
    """Get count of orders for each customer."""
    return (
        db.query(Customer.name, func.count(Order.id))
        .join(Order)
        .group_by(Customer.id)
        .all()
    )

def get_popular_cake_flavors(db: Session, limit: int = 5) -> List[Tuple[str, int]]:
    """Get most popular cake flavors."""
    return (
        db.query(OrderDetail.flavor, func.count(OrderDetail.id))
        .group_by(OrderDetail.flavor)
        .order_by(func.count(OrderDetail.id).desc())
        .limit(limit)
        .all()
    )

def get_average_order_value(db: Session) -> float:
    """Get average order value."""
    return (
        db.query(func.avg(Order.total_amount))
        .scalar() or 0.0
    )

def get_customer_chat_history(db: Session, customer_id: int) -> List[ChatHistory]:
    """Get all chat history for a specific customer."""
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.customer_id == customer_id)
        .order_by(ChatHistory.timestamp)
        .all()
    )