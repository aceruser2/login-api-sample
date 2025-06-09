from sqlalchemy.orm import Session
from sqlalchemy import select
from app.model import Order, OrderItem, MenuItem
from app.schema import OrderCreate, OrderUpdate


def create_order(db: Session, order: OrderCreate):
    """Create a new order with items"""
    # Calculate total amount from items
    total = 0
    order_items = []

    for item in order.items:
        menu_item = db.execute(
            select(MenuItem).where(MenuItem.uuid == item.item_uuid)
        ).scalar_one_or_none()

        if not menu_item:
            raise ValueError(f"Menu item {item.item_uuid} not found")

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

    # Create order
    db_order = Order(
        customer_uuid=order.customer_uuid,
        desk_uuid=order.desk_uuid,
        total_amount=total,
        status="pending",
        order_type=order.order_type,
        note=order.note,
    )
    db.add(db_order)
    db.flush()

    # Create order items
    for item in order_items:
        db_item = OrderItem(order_uuid=db_order.uuid, **item)
        db.add(db_item)

    return db_order


def get_orders(db: Session, skip: int = 0, limit: int = 20, status: str = None):
    """Get all orders with optional status filter"""
    query = select(Order).where(Order.soft_delete == False)
    if status:
        query = query.where(Order.status == status)
    return db.execute(query.offset(skip).limit(limit)).scalars().all()


def update_order_status(db: Session, order_uuid: str, status: str):
    """Update order status"""
    db_order = db.execute(
        select(Order).where(Order.uuid == order_uuid)
    ).scalar_one_or_none()

    if not db_order:
        raise ValueError("Order not found")

    db_order.status = status
    return db_order


def get_order_by_uuid(db: Session, order_uuid: str):
    """Get order by UUID"""
    return db.execute(
        select(Order).where(Order.uuid == order_uuid)
    ).scalar_one_or_none()
