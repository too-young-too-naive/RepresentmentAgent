from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.db import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(20))
    address = Column(String(500))
    account_created_at = Column(DateTime, nullable=False)

    orders = relationship("Order", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    amount = Column(Float, nullable=False)
    item_description = Column(String(500), nullable=False)
    order_date = Column(DateTime, nullable=False)
    shipping_status = Column(String(50), nullable=False)
    tracking_number = Column(String(100))
    delivery_date = Column(DateTime)

    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    card_last_four = Column(String(4), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    bank_name = Column(String(100), nullable=False)

    order = relationship("Order", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")


class Chargeback(Base):
    __tablename__ = "chargebacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), unique=True, nullable=False)
    bank_name = Column(String(100), nullable=False)
    cardholder_name = Column(String(200), nullable=False)
    card_last_four = Column(String(4), nullable=False)
    transaction_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    reason_code = Column(String(100), nullable=False)
    cardholder_statement = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="new")
    decision = Column(String(50))
    representment_note = Column(Text)
    evidence_summary = Column(Text)
    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)
