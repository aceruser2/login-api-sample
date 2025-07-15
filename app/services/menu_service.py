from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from app.model import MenuItem
from app.schema import MenuItemCreate, MenuItemUpdate
from typing import List, Optional


def create_menu_item(db: Session, item: MenuItemCreate):
    """創建菜單項目"""
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    return db_item


def get_menu_items(
    db: Session, skip: int = 0, limit: int = 20, category: Optional[str] = None
) -> List[MenuItem]:
    """獲取菜單項目列表"""
    stmt = (
        select(MenuItem).where(MenuItem.soft_delete == False).offset(skip).limit(limit)
    )
    if category:
        stmt = stmt.where(MenuItem.category == category)
    return db.execute(stmt).scalars().all()


def get_menu_items_with_inventory(
    db: Session, skip: int = 0, limit: int = 20, category: Optional[str] = None
):
    """獲取帶庫存信息的菜單項目"""
    stmt = select(MenuItem).where(MenuItem.soft_delete == False)
    if category:
        stmt = stmt.where(MenuItem.category == category)

    items = db.execute(stmt.offset(skip).limit(limit)).scalars().all()

    # 增加庫存狀態檢查
    for item in items:
        # 如果庫存量為0，自動設置不可用
        if hasattr(item, "stock_quantity") and item.stock_quantity <= 0:
            item.available = False

    return items


def update_menu_item(db: Session, item_uuid: str, item: MenuItemUpdate):
    """更新菜單項目"""
    stmt = select(MenuItem).where(
        MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
    )
    db_item = db.execute(stmt).scalar_one_or_none()

    if not db_item:
        raise ValueError("Menu item not found")

    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    return db_item


def update_item_inventory(db: Session, item_uuid: str, quantity: int):
    """更新商品庫存"""
    stmt = select(MenuItem).where(
        MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
    )
    item = db.execute(stmt).scalar_one_or_none()

    if not item:
        raise ValueError(f"Menu item {item_uuid} not found")

    if not hasattr(item, "stock_quantity"):
        # 如果未設置庫存字段，添加此字段
        item.stock_quantity = 100  # 默認庫存

    # 確保庫存足夠
    if item.stock_quantity < quantity:
        raise ValueError(
            f"Insufficient inventory for {item.name}. Available: {item.stock_quantity}"
        )

    # 更新庫存
    item.stock_quantity -= quantity

    # 如果庫存為0，設置商品不可用
    if item.stock_quantity <= 0:
        item.available = False

    return item


def delete_menu_item(db: Session, item_uuid: str):
    """軟刪除菜單項目"""
    stmt = select(MenuItem).where(
        MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
    )
    item = db.execute(stmt).scalar_one_or_none()

    if not item:
        raise ValueError("Menu item not found")

    item.soft_delete = True
    item.update_dt = datetime.now()
    return item
