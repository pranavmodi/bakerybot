from typing import List, Dict, Optional, Union
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.database import Order, Customer, OrderStatus, Product

load_dotenv()

def verify_admin_password(password: str) -> Dict[str, bool]:
    """
    Verify if the provided password matches the admin password stored in environment variables.

    Args:
        password (str): The password to verify against the admin password.

    Returns:
        Dict[str, bool]: A dictionary containing a single key 'is_valid' with a boolean value.
            - True if the password matches
            - False if the password doesn't match

    Example:
        >>> result = verify_admin_password("admin123")
        >>> print(result)
        {'is_valid': True}
    """
    correct_password = os.getenv('ADMIN_PASSWORD')
    return {"is_valid": password == correct_password}

def view_all_orders(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Optional[Session] = None) -> List[Dict]:
    """
    View all orders within a specified date range.

    Args:
        start_date (Optional[datetime]): The start date to filter orders from. If None, no start date filter is applied.
        end_date (Optional[datetime]): The end date to filter orders until. If None, no end date filter is applied.
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        List[Dict]: A list of order dictionaries, each containing order details like:
            - order_id
            - customer_id
            - status
            - total_amount
            - created_at
            - etc.

    Example:
        >>> from datetime import datetime, timedelta
        >>> start = datetime.now() - timedelta(days=7)
        >>> orders = view_all_orders(start_date=start)
    """
    if db is None:
        with SessionLocal() as db:
            return _view_all_orders(start_date, end_date, db)
    return _view_all_orders(start_date, end_date, db)

def _view_all_orders(start_date: Optional[datetime], end_date: Optional[datetime], db: Session) -> List[Dict]:
    """
    Internal function to handle order viewing logic with database operations.

    Args:
        start_date (Optional[datetime]): The start date to filter orders from
        end_date (Optional[datetime]): The end date to filter orders until
        db (Session): SQLAlchemy database session

    Returns:
        List[Dict]: A list of order dictionaries with full order details
    """
    query = db.query(Order)
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    orders = query.all()
    return [order.to_dict() for order in orders]

def update_product_price(product_id: int, new_price: float, db: Optional[Session] = None) -> bool:
    """
    Update the price of a specific product in the inventory.

    Args:
        product_id (int): The unique identifier of the product to update
        new_price (float): The new price to set for the product
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        bool: True if the price was successfully updated, False if the product wasn't found

    Example:
        >>> success = update_product_price(product_id=1, new_price=9.99)
        >>> print(success)
        True
    """
    if db is None:
        with SessionLocal() as db:
            return _update_product_price(product_id, new_price, db)
    return _update_product_price(product_id, new_price, db)

def _update_product_price(product_id: int, new_price: float, db: Session) -> bool:
    """
    Internal function to handle product price update logic with database operations.

    Args:
        product_id (int): The unique identifier of the product
        new_price (float): The new price to set
        db (Session): SQLAlchemy database session

    Returns:
        bool: True if update successful, False if product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    product.price = new_price
    db.commit()
    return True

def add_new_product(name: str, price: float, description: str, quantity: int, db: Optional[Session] = None) -> Dict:
    """
    Add a new product to the bakery's inventory.

    Args:
        name (str): The name of the product
        price (float): The price of the product
        description (str): A detailed description of the product
        quantity (int): Initial stock quantity of the product
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        Dict: A dictionary containing the newly created product's details including:
            - id: The unique identifier
            - name: Product name
            - price: Product price
            - description: Product description
            - quantity: Available quantity

    Example:
        >>> product = add_new_product(
        ...     name="Chocolate Croissant",
        ...     price=3.99,
        ...     description="Buttery croissant filled with chocolate",
        ...     quantity=50
        ... )
    """
    if db is None:
        with SessionLocal() as db:
            return _add_new_product(name, price, description, quantity, db)
    return _add_new_product(name, price, description, quantity, db)

def _add_new_product(name: str, price: float, description: str, quantity: int, db: Session) -> Dict:
    """
    Internal function to handle new product addition logic with database operations.

    Args:
        name (str): Product name
        price (float): Product price
        description (str): Product description
        quantity (int): Initial stock quantity
        db (Session): SQLAlchemy database session

    Returns:
        Dict: Dictionary containing the new product's details
    """
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
    """
    Remove a product from the bakery's inventory.

    Args:
        product_id (int): The unique identifier of the product to remove
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        bool: True if the product was successfully removed, False if the product wasn't found

    Example:
        >>> success = remove_product(product_id=1)
        >>> print(success)
        True
    """
    if db is None:
        with SessionLocal() as db:
            return _remove_product(product_id, db)
    return _remove_product(product_id, db)

def _remove_product(product_id: int, db: Session) -> bool:
    """
    Internal function to handle product removal logic with database operations.

    Args:
        product_id (int): The unique identifier of the product
        db (Session): SQLAlchemy database session

    Returns:
        bool: True if removal successful, False if product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True

def view_customer_history(customer_id: int, db: Optional[Session] = None) -> List[Dict]:
    """
    View the complete order history for a specific customer.

    Args:
        customer_id (int): The unique identifier of the customer
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        List[Dict]: A list of dictionaries containing order details for the customer, including:
            - order_id
            - status
            - total_amount
            - created_at
            - items ordered
            - etc.

    Example:
        >>> history = view_customer_history(customer_id=123)
        >>> for order in history:
        ...     print(f"Order {order['order_id']}: ${order['total_amount']}")
    """
    if db is None:
        with SessionLocal() as db:
            return _view_customer_history(customer_id, db)
    return _view_customer_history(customer_id, db)

def _view_customer_history(customer_id: int, db: Session) -> List[Dict]:
    """
    Internal function to handle customer history viewing logic with database operations.

    Args:
        customer_id (int): The unique identifier of the customer
        db (Session): SQLAlchemy database session

    Returns:
        List[Dict]: List of order dictionaries for the customer
    """
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return [order.to_dict() for order in orders]

def get_daily_sales_report(date: datetime, db: Optional[Session] = None) -> Dict:
    """
    Generate a comprehensive sales report for a specific date.

    Args:
        date (datetime): The date to generate the report for
        db (Optional[Session]): SQLAlchemy database session. If None, a new session will be created.

    Returns:
        Dict: A dictionary containing the daily sales report with:
            - date (str): The date of the report in YYYY-MM-DD format
            - total_sales (float): Total revenue for the day
            - number_of_orders (int): Total number of orders processed
            - orders (List[Dict]): Detailed list of all orders for the day

    Example:
        >>> from datetime import datetime
        >>> report = get_daily_sales_report(datetime.now())
        >>> print(f"Total sales: ${report['total_sales']}")
        >>> print(f"Number of orders: {report['number_of_orders']}")
    """
    if db is None:
        with SessionLocal() as db:
            return _get_daily_sales_report(date, db)
    return _get_daily_sales_report(date, db)

def _get_daily_sales_report(date: datetime, db: Session) -> Dict:
    """
    Internal function to handle daily sales report generation with database operations.

    Args:
        date (datetime): The date to generate the report for
        db (Session): SQLAlchemy database session

    Returns:
        Dict: Dictionary containing the daily sales report details
    """
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
