from sqlalchemy.orm import Session
from sqlalchemy import select
from app.model import Order, OrderItem, MenuItem
from app.schema import OrderCreate, OrderUpdate
from app.extension.emun_setting import OrderStatusEnum
from app.services.inventory_service import (
    check_inventory_availability,
    deduct_inventory,
)


def create_order(db: Session, order: OrderCreate):
    """Create a new order with items"""
    # Calculate total amount from items
    total = 0
    order_items = []

    # 檢查所有訂單項的庫存
    for item in order.items:
        stmt = select(MenuItem).where(MenuItem.uuid == item.item_uuid)
        menu_item = db.execute(stmt).scalar_one_or_none()

        if not menu_item:
            raise ValueError(f"Menu item {item.item_uuid} not found")

        # 檢查庫存
        if not check_inventory_availability(db, item.item_uuid, item.quantity):
            raise ValueError(f"Insufficient inventory for {menu_item.name}")

        subtotal = menu_item.price * item.quantity
        total += subtotal

        order_items.append(
            {
                "item_uuid": item.item_uuid,
                "quantity": item.quantity,
                "unit_price": menu_item.price,
                "subtotal": subtotal,
                "note": item.note,
                "status": OrderStatusEnum.PENDING.value,
            }
        )

    # Create order
    db_order = Order(
        customer_uuid=order.customer_uuid,
        desk_uuid=order.desk_uuid,
        total_amount=total,
        status=OrderStatusEnum.PENDING.value,
        order_type=order.order_type,
        note=order.note,
    )
    db.add(db_order)
    db.flush()

    # Create order items and deduct inventory
    for item_data in order_items:
        db_item = OrderItem(order_uuid=db_order.uuid, **item_data)
        db.add(db_item)
        # 扣減庫存
        deduct_inventory(db, item_data["item_uuid"], item_data["quantity"])

    return db_order


def get_orders(db: Session, skip: int = 0, limit: int = 20, status: str = None):
    """Get all orders with optional status filter"""
    stmt = select(Order).where(Order.soft_delete == False)
    if status:
        stmt = stmt.where(Order.status == status)
    return db.execute(stmt.offset(skip).limit(limit)).scalars().all()


def update_order_status(db: Session, order_uuid: str, status: str):
    """Update order status"""
    stmt = select(Order).where(Order.uuid == order_uuid)
    db_order = db.execute(stmt).scalar_one_or_none()

    if not db_order:
        raise ValueError("Order not found")

    db_order.status = status
    return db_order


def get_order_by_uuid(db: Session, order_uuid: str):
    """Get order by UUID"""
    stmt = select(Order).where(Order.uuid == order_uuid)
    return db.execute(stmt).scalar_one_or_none()
        select(Order).where(Order.uuid == order_uuid)
    ).scalar_one_or_none()
