from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import Customer, Order, OrderDetail, ChatHistory, OrderStatus

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    # Customer operations
    def get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.phone_number == phone_number).first()

    def create_customer(self, phone_number: str, name: Optional[str] = None, preferences: Optional[Dict] = None) -> Customer:
        customer = Customer(
            phone_number=phone_number,
            name=name,
            preferences=preferences or {}
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update_customer_preferences(self, customer_id: int, preferences: Dict) -> Customer:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.preferences.update(preferences)
            self.db.commit()
            self.db.refresh(customer)
        return customer

    def update_customer_name(self, customer_id: int, name: str) -> Optional[Customer]:
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.name = name
            self.db.commit()
            self.db.refresh(customer)
        return customer

    # Order operations
    def create_order(self, 
                    customer_id: int, 
                    order_type: str,
                    total_amount: float,
                    pickup_time: datetime) -> Order:
        order = Order(
            customer_id=customer_id,
            type=order_type,
            total_amount=total_amount,
            pickup_time=pickup_time,
            status=OrderStatus.PENDING,
            payment_status="pending"
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        order = self.get_order(order_id)
        if order:
            order.status = status
            self.db.commit()
            self.db.refresh(order)
        return order

    def update_payment_status(self, order_id: int, payment_status: str) -> Optional[Order]:
        order = self.get_order(order_id)
        if order:
            order.payment_status = payment_status
            self.db.commit()
            self.db.refresh(order)
        return order

    # Order Detail operations
    def create_order_detail(self,
                          order_id: int,
                          cake_name: str,
                          size: str,
                          tiers: int,
                          flavor: str,
                          filling: str,
                          frosting: str,
                          dietary_restrictions: Dict,
                          message: Optional[str] = None,
                          special_instructions: Optional[str] = None) -> OrderDetail:
        detail = OrderDetail(
            order_id=order_id,
            cake_name=cake_name,
            size=size,
            tiers=tiers,
            flavor=flavor,
            filling=filling,
            frosting=frosting,
            dietary_restrictions=dietary_restrictions,
            message=message,
            special_instructions=special_instructions
        )
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        return detail

    # Chat History operations
    def add_chat_history(self,
                        customer_id: int,
                        user_message: str,
                        bot_response: str,
                        context: Optional[Dict] = None) -> ChatHistory:
        chat = ChatHistory(
            customer_id=customer_id,
            user_message=user_message,
            bot_response=bot_response,
            context=context or {}
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_customer_chat_history(self, customer_id: int, limit: int = 10) -> List[ChatHistory]:
        return self.db.query(ChatHistory)\
            .filter(ChatHistory.customer_id == customer_id)\
            .order_by(ChatHistory.timestamp.desc())\
            .limit(limit)\
            .all()

    # Utility methods
    def get_customer_orders(self, customer_id: int, limit: int = 5) -> List[Order]:
        return self.db.query(Order)\
            .filter(Order.customer_id == customer_id)\
            .order_by(Order.created_at.desc())\
            .limit(limit)\
            .all() 