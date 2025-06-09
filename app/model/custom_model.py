from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from app.model.base import Base, PGPEncryptString


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    customer_name = Column(PGPEncryptString())
    customer_phone = Column(PGPEncryptString())
    email = Column(PGPEncryptString(), unique=True)
    is_verified = Column(Boolean, default=False)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
