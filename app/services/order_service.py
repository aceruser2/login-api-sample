from sqlalchemy.orm import Session
from sqlalchemy import select
from app.model import Order, OrderItem, MenuItem
from app.schema import OrderCreate, OrderUpdate
from app.extension.emun_setting import OrderStatusEnum
from datetime import datetime, timezone


def create_order(db: Session, order: OrderCreate):
    """創建新訂單"""
    # 計算總金額
    total = 0
    order_items = []

    # 檢查所有訂單項的庫存和價格
    for item in order.items:
        stmt = select(MenuItem).where(MenuItem.uuid == item.item_uuid)
        menu_item = db.execute(stmt).scalar_one_or_none()

        if not menu_item:
            raise ValueError(f"Menu item {item.item_uuid} not found")

        if not menu_item.available:
            raise ValueError(f"Menu item {menu_item.name} is not available")

        subtotal = menu_item.price * item.quantity
        total += subtotal

        order_items.append(
            {
                "item_uuid": item.item_uuid,
                "quantity": item.quantity,
                "unit_price": menu_item.price,
                "subtotal": subtotal,
                "note": item.note,
                "status": "pending",
            }
        )

    # 創建訂單
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

    # 創建訂單項目
    for item_data in order_items:
        db_item = OrderItem(order_uuid=db_order.uuid, **item_data)
        db.add(db_item)

    return db_order


def get_orders(db: Session, skip: int = 0, limit: int = 20, status: str = None):
    """獲取訂單列表"""
    stmt = select(Order).where(Order.soft_delete == False)
    if status:
        stmt = stmt.where(Order.status == status)
    return db.execute(stmt.offset(skip).limit(limit)).scalars().all()


def update_order_status(db: Session, order_uuid: str, status: str):
    """更新訂單狀態"""
    stmt = select(Order).where(Order.uuid == order_uuid)
    db_order = db.execute(stmt).scalar_one_or_none()

    if not db_order:
        raise ValueError("Order not found")

    db_order.status = status
    db_order.update_dt = datetime.now()
    return db_order


def get_order_by_uuid(db: Session, order_uuid: str):
    """通過UUID獲取訂單"""
    stmt = select(Order).where(Order.uuid == order_uuid)
    return db.execute(stmt).scalar_one_or_none()


def get_orders_by_customer(
    db: Session, customer_uuid: str, skip: int = 0, limit: int = 20
):
    """獲取特定顧客的訂單"""
    stmt = (
        select(Order)
        .where(Order.customer_uuid == customer_uuid, Order.soft_delete == False)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def update_order(db: Session, order_uuid: str, order_update: OrderUpdate):
    """更新訂單內容（僅pending狀態）"""
    stmt = select(Order).where(Order.uuid == order_uuid)
    db_order = db.execute(stmt).scalar_one_or_none()

    if not db_order:
        raise ValueError("Order not found")

    # 只有pending狀態的訂單可以被更新
    if db_order.status != OrderStatusEnum.PENDING.value:
        raise ValueError("Can only update pending orders")

    # 更新訂單基本信息
    if order_update.note is not None:
        db_order.note = order_update.note

    # 如果有更新訂單項目
    if order_update.items:
        # 刪除現有訂單項目
        stmt = select(OrderItem).where(OrderItem.order_uuid == order_uuid)
        existing_items = db.execute(stmt).scalars().all()
        for item in existing_items:
            db.delete(item)

        # 重新計算總額和添加新項目
        total = 0
        for item in order_update.items:
            stmt = select(MenuItem).where(MenuItem.uuid == item.item_uuid)
            menu_item = db.execute(stmt).scalar_one_or_none()

            if not menu_item:
                raise ValueError(f"Menu item {item.item_uuid} not found")

            if not menu_item.available:
                raise ValueError(f"Menu item {menu_item.name} is not available")

            subtotal = menu_item.price * item.quantity
            total += subtotal

            db_item = OrderItem(
                order_uuid=order_uuid,
                item_uuid=item.item_uuid,
                quantity=item.quantity,
                unit_price=menu_item.price,
                subtotal=subtotal,
                note=item.note,
                status="pending",
            )
            db.add(db_item)

        db_order.total_amount = total

    db_order.update_dt = datetime.now(timezone.utc)
    return db_order
