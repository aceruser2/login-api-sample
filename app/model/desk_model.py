from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from app.model.base import Base


class Desk(Base):
    __tablename__ = "desks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    desk_name = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class DeskCustomer(Base):
    __tablename__ = "desk_customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    desk_uuid = Column(String)
    customer_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
