from sqlalchemy.orm import Session
from sqlalchemy import select
from app.model import MenuItem
from app.schema import MenuItemCreate, MenuItemUpdate


def create_menu_item(db: Session, item: MenuItemCreate):
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    return db_item


def get_menu_items(db: Session, skip: int = 0, limit: int = 20, category: str = None):
    query = select(MenuItem).where(MenuItem.soft_delete == False)
    if category:
        query = query.where(MenuItem.category == category)
    return db.execute(query.offset(skip).limit(limit)).scalars().all()


def update_menu_item(db: Session, item_uuid: str, item: MenuItemUpdate):
    db_item = db.execute(
        select(MenuItem).where(
            MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
        )
    ).scalar_one_or_none()

    if not db_item:
        raise ValueError("Menu item not found")

    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    return db_item
