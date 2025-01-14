from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "quantity": self.quantity
        }

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False)
    name = Column(String)
    preferences = Column(JSON)  # Store dietary preferences, favorite flavors etc
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    type = Column(String)  # 'immediate' or 'custom'
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float)
    payment_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    pickup_time = Column(DateTime)
    summary = Column(Text)  # Store a brief summary/overview of the order
    
    customer = relationship("Customer", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

    def to_dict(self) -> dict:
        """Convert Order object to dictionary.
        
        Returns:
            dict: Dictionary containing order details
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "type": self.type,
            "status": self.status.value if self.status else None,
            "total_amount": self.total_amount,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "pickup_time": self.pickup_time.isoformat() if self.pickup_time else None,
            "summary": self.summary,
            "details": [detail.to_dict() for detail in self.details] if self.details else []
        }

class OrderDetail(Base):
    __tablename__ = "order_details"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    cake_name = Column(String)
    size = Column(String)
    tiers = Column(Integer)
    flavor = Column(String)
    filling = Column(String)
    frosting = Column(String)
    dietary_restrictions = Column(JSON)
    message = Column(Text)
    special_instructions = Column(Text)
    
    order = relationship("Order", back_populates="details")

    def to_dict(self) -> dict:
        """Convert OrderDetail object to dictionary.
        
        Returns:
            dict: Dictionary containing order detail information
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "cake_name": self.cake_name,
            "size": self.size,
            "tiers": self.tiers,
            "flavor": self.flavor,
            "filling": self.filling,
            "frosting": self.frosting,
            "dietary_restrictions": self.dietary_restrictions,
            "message": self.message,
            "special_instructions": self.special_instructions
        }

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    context = Column(JSON)  # Store conversation context 