from sqlalchemy.orm import Session
from sqlalchemy import select
from app.model import Inventory, MenuItem
from datetime import datetime


def get_inventory_by_menu_item(db: Session, menu_item_uuid: str):
    """獲取指定菜單項的庫存情況"""
    stmt = select(Inventory).where(
        Inventory.menu_item_uuid == menu_item_uuid, Inventory.soft_delete == False
    )
    return db.execute(stmt).scalar_one_or_none()


def check_inventory_availability(
    db: Session, menu_item_uuid: str, required_quantity: int
) -> bool:
    """檢查庫存是否足夠"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)
    if not inventory:
        # 如果沒有庫存記錄，預設可用
        return True

    return inventory.stock_quantity >= required_quantity


def deduct_inventory(db: Session, menu_item_uuid: str, quantity: int):
    """扣減庫存"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)

    if not inventory:
        # 如果沒有庫存記錄，創建一個預設記錄
        inventory = Inventory(
            menu_item_uuid=menu_item_uuid,
            stock_quantity=100,  # 預設庫存
            low_stock_threshold=5,
        )
        db.add(inventory)
        db.flush()

    if inventory.stock_quantity < quantity:
        raise ValueError(f"Insufficient stock for item {menu_item_uuid}")

    inventory.stock_quantity -= quantity
    inventory.update_dt = datetime.now()

    return inventory


def update_inventory(db: Session, menu_item_uuid: str, new_quantity: int):
    """更新庫存數量"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)

    if not inventory:
        inventory = Inventory(
            menu_item_uuid=menu_item_uuid,
            stock_quantity=new_quantity,
            low_stock_threshold=5,
        )
        db.add(inventory)
    else:
        inventory.stock_quantity = new_quantity
        inventory.update_dt = datetime.now()

    return inventory


def get_low_stock_items(db: Session, skip: int = 0, limit: int = 20):
    """獲取低庫存商品"""
    stmt = (
        select(Inventory, MenuItem)
        .join(MenuItem, MenuItem.uuid == Inventory.menu_item_uuid)
        .where(
            Inventory.stock_quantity <= Inventory.low_stock_threshold,
            Inventory.soft_delete == False,
            MenuItem.soft_delete == False,
        )
        .offset(skip)
        .limit(limit)
    )

    return db.execute(stmt).all()
