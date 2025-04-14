from sqlalchemy.orm import Session
from sqlalchemy import select
from app.adapter.model import MenuItem
from app.adapter.schema import MenuItemCreate, MenuItemUpdate
from fastapi import HTTPException


def create_menu_item(db: Session, item: MenuItemCreate):
    db_item = MenuItem(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


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
        raise HTTPException(status_code=404, detail="Menu item not found")

    for field, value in item.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    return db_item
