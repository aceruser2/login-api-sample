from sqlalchemy.orm import Session
from sqlalchemy import select, outerjoin
from datetime import datetime
from app.model import MenuItem, Inventory
from app.schema import MenuItemCreate, MenuItemUpdate, MenuItemWithInventory


def create_menu_item(db: Session, item: MenuItemCreate):
    db_item = MenuItem(**item.model_dump())
    db.add(db_item)
    return db_item


def get_menu_items(db: Session, skip: int = 0, limit: int = 20, category: str = None):
    query = select(MenuItem).where(MenuItem.soft_delete == False)
    if category:
        query = query.where(MenuItem.category == category)
    return db.execute(query.offset(skip).limit(limit)).scalars().all()


def get_menu_items_with_inventory(
    db: Session, skip: int = 0, limit: int = 20, category: str = None
):
    """獲取帶庫存信息的菜單項目"""
    query = select(MenuItem).where(MenuItem.soft_delete == False)
    if category:
        query = query.where(MenuItem.category == category)

    items = db.execute(query.offset(skip).limit(limit)).scalars().all()

    # 增加庫存狀態檢查
    for item in items:
        # 如果庫存量為0，自動設置不可用
        if hasattr(item, "stock_quantity") and item.stock_quantity <= 0:
            item.available = False

    return items


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


def update_item_inventory(db: Session, item_uuid: str, quantity: int):
    """更新商品庫存"""
    item = db.execute(
        select(MenuItem).where(
            MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
        )
    ).scalar_one_or_none()

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
    item = db.execute(
        select(MenuItem).where(
            MenuItem.uuid == item_uuid, MenuItem.soft_delete == False
        )
    ).scalar_one_or_none()

    if not item:
        raise ValueError("Menu item not found")

    item.soft_delete = True
    item.update_dt = datetime.now()
    return item
