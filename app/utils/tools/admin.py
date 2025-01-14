from typing import List, Dict, Optional, Union
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.database import Order, Customer, OrderStatus, Product

load_dotenv()

def verify_admin_password(password: str) -> Dict[str, bool]:
    """Verify if the provided password matches the admin password"""
    correct_password = os.getenv('ADMIN_PASSWORD')
    print(correct_password)
    return {"is_valid": password == correct_password}

def view_all_orders(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Optional[Session] = None) -> List[Dict]:
    """View all orders within a date range"""
    if db is None:
        with SessionLocal() as db:
            return _view_all_orders(start_date, end_date, db)
    return _view_all_orders(start_date, end_date, db)

def _view_all_orders(start_date: Optional[datetime], end_date: Optional[datetime], db: Session) -> List[Dict]:
    """Internal function to handle order viewing logic"""
    query = db.query(Order)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    orders = query.all()
    return [order.to_dict() for order in orders]

def update_product_price(product_id: int, new_price: float, db: Optional[Session] = None) -> bool:
    """Update the price of a product"""
    if db is None:
        with SessionLocal() as db:
            return _update_product_price(product_id, new_price, db)
    return _update_product_price(product_id, new_price, db)

def _update_product_price(product_id: int, new_price: float, db: Session) -> bool:
    """Internal function to handle price update logic"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    product.price = new_price
    db.commit()
    return True

def add_new_product(name: str, price: float, description: str, quantity: int, db: Optional[Session] = None) -> Dict:
    """Add a new product to the inventory"""
    if db is None:
        with SessionLocal() as db:
            return _add_new_product(name, price, description, quantity, db)
    return _add_new_product(name, price, description, quantity, db)

def _add_new_product(name: str, price: float, description: str, quantity: int, db: Session) -> Dict:
    """Internal function to handle product addition logic"""
    product = Product(
        name=name,
        price=price,
        description=description,
        quantity=quantity
    )
    db.add(product)
    db.commit()
    return product.to_dict()

def remove_product(product_id: int, db: Optional[Session] = None) -> bool:
    """Remove a product from the inventory"""
    if db is None:
        with SessionLocal() as db:
            return _remove_product(product_id, db)
    return _remove_product(product_id, db)

def _remove_product(product_id: int, db: Session) -> bool:
    """Internal function to handle product removal logic"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True

def view_customer_history(customer_id: int, db: Optional[Session] = None) -> List[Dict]:
    """View order history for a specific customer"""
    if db is None:
        with SessionLocal() as db:
            return _view_customer_history(customer_id, db)
    return _view_customer_history(customer_id, db)

def _view_customer_history(customer_id: int, db: Session) -> List[Dict]:
    """Internal function to handle customer history viewing logic"""
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return [order.to_dict() for order in orders]

def get_daily_sales_report(date: datetime, db: Optional[Session] = None) -> Dict:
    """Get sales report for a specific date"""
    if db is None:
        with SessionLocal() as db:
            return _get_daily_sales_report(date, db)
    return _get_daily_sales_report(date, db)

def _get_daily_sales_report(date: datetime, db: Session) -> Dict:
    """Internal function to handle daily sales report logic"""
    orders = db.query(Order).filter(
        Order.created_at >= date.replace(hour=0, minute=0, second=0),
        Order.created_at < date.replace(hour=23, minute=59, second=59)
    ).all()
    
    total_sales = sum(order.total_amount for order in orders)
    num_orders = len(orders)
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "total_sales": total_sales,
        "number_of_orders": num_orders,
        "orders": [order.to_dict() for order in orders]
    }
