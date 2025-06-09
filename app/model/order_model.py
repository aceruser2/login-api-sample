from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from app.model.base import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    customer_uuid = Column(String)
    desk_uuid = Column(String)
    total_amount = Column(Integer, default=0)
    status = Column(Integer)
    order_type = Column(String)
    note = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    order_uuid = Column(String)
    item_uuid = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Integer)
    subtotal = Column(Integer)
    note = Column(String)
    status = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    ingredient_uuid = Column(String)
    quantity = Column(Integer)
    stock_type = Column(Integer)
    note = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
