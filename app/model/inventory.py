from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from app.model.base import Base


class Inventory(Base):
    """庫存管理表"""

    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    menu_item_uuid = Column(String, nullable=False)  # 純UUID外鍵，不使用ForeignKey
    stock_quantity = Column(Integer, nullable=False, default=0)  # 剩餘庫存
    low_stock_threshold = Column(Integer, nullable=False, default=5)  # 低庫存閾值
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
    soft_delete = Column(Boolean, default=False)
