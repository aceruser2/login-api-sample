from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from app.model.base import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    order_uuid = Column(String)
    payment_method = Column(String)
    amount_paid = Column(Integer)
    payment_note = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
