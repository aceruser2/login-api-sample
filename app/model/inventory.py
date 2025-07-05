from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.model.base import Base
import uuid


class Inventory(Base):
    """庫存管理表"""

    __tablename__ = "inventory"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_uuid = Column(
        UUID(as_uuid=True), ForeignKey("menu_items.uuid"), nullable=False
    )
    stock_quantity = Column(Integer, nullable=False, default=0)  # 剩餘庫存
    low_stock_threshold = Column(Integer, nullable=False, default=5)  # 低庫存閾值
    update_dt = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    soft_delete = Column(Boolean, default=False)

    # 關聯菜單項
    menu_item = relationship("MenuItem", back_populates="inventory")
