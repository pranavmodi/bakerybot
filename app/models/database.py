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
    
    customer = relationship("Customer", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

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

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    context = Column(JSON)  # Store conversation context 