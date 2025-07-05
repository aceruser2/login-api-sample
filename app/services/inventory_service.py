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
    db: Session, menu_item_uuid: str, quantity: int
) -> bool:
    """檢查庫存是否充足"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)
    if not inventory:
        return False
    return inventory.stock_quantity >= quantity


def deduct_inventory(db: Session, menu_item_uuid: str, quantity: int) -> bool:
    """扣減庫存"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)
    if not inventory or inventory.stock_quantity < quantity:
        raise ValueError(f"庫存不足: {menu_item_uuid}")

    # 扣減庫存
    inventory.stock_quantity -= quantity
    inventory.update_dt = datetime.now()
    return True


def update_inventory(db: Session, menu_item_uuid: str, quantity: int) -> Inventory:
    """更新庫存數量"""
    inventory = get_inventory_by_menu_item(db, menu_item_uuid)
    if not inventory:
        # 如果不存在則創建新的庫存記錄
        inventory = Inventory(menu_item_uuid=menu_item_uuid, stock_quantity=quantity)
        db.add(inventory)
    else:
        inventory.stock_quantity = quantity
        inventory.update_dt = datetime.now()

    return inventory
