from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Integer, default=1)

    # 添加庫存關聯
    inventory = relationship("Inventory", back_populates="menu_item", uselist=False)
