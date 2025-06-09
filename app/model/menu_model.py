from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from app.model.base import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    category = Column(String)
    image_url = Column(String)
    available = Column(Boolean, default=True)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    unit = Column(String)
    min_stock = Column(Integer)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class MenuItemIngredient(Base):
    __tablename__ = "menu_item_ingredients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    menu_item_uuid = Column(String)
    ingredient_uuid = Column(String)
    quantity = Column(Integer)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
