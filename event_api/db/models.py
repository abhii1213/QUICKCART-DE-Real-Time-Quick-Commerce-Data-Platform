from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from event_api.db.postgres import Base


class User(Base):
    """
    Customer accounts
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    city = Column(String)
    area = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    """
    Product catalog
    """
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    price = Column(Float)
    stock_qty = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    """
    Order master record
    """
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_amount = Column(Float)
    payment_mode = Column(String)
    order_status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderItem(Base):
    """
    Order line items
    """
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"))
    product_id = Column(String, ForeignKey("products.product_id"))
    qty = Column(Integer)
    unit_price = Column(Float)
    line_total = Column(Float)