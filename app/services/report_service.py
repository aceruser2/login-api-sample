from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, and_, text
from datetime import datetime, timedelta
from app.model import Order, OrderItem, MenuItem, Payment
from typing import List, Dict, Any
import logging

log = logging.getLogger(__name__)


def get_daily_sales(db: Session, date: datetime) -> Dict[str, Any]:
    """獲取指定日期的銷售報表"""
    # 設定日期範圍
    start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_date = start_date + timedelta(days=1)

    # 查詢訂單數量和總金額
    orders_query = select(
        func.count(Order.uuid).label("order_count"),
        func.sum(Order.total_amount).label("total_sales"),
    ).where(
        Order.create_dt >= start_date,
        Order.create_dt < end_date,
        Order.status == "completed",  # 只計算已完成訂單
        Order.soft_delete == False,
    )

    result = db.execute(orders_query).first()
    order_count = result[0] or 0
    total_sales = float(result[1]) if result[1] else 0

    # 計算平均訂單金額
    avg_order_amount = total_sales / order_count if order_count > 0 else 0

    # 按支付方式分類
    payment_methods = db.execute(
        select(
            Payment.payment_method,
            func.count(Payment.uuid),
            func.sum(Payment.amount_paid),
        )
        .join(Order, Payment.order_uuid == Order.uuid)
        .where(
            Order.create_dt >= start_date,
            Order.create_dt < end_date,
            Order.soft_delete == False,
            Payment.soft_delete == False,
        )
        .group_by(Payment.payment_method)
    ).all()

    payment_breakdown = [
        {"method": method, "count": count, "amount": float(amount) if amount else 0}
        for method, count, amount in payment_methods
    ]

    # 按時段分布
    hourly_sales = db.execute(
        select(
            func.extract("hour", Order.create_dt).label("hour"),
            func.count(Order.uuid),
            func.sum(Order.total_amount),
        )
        .where(
            Order.create_dt >= start_date,
            Order.create_dt < end_date,
            Order.status == "completed",
            Order.soft_delete == False,
        )
        .group_by(text("hour"))
        .order_by(text("hour"))
    ).all()

    hourly_breakdown = [
        {"hour": int(hour), "count": count, "amount": float(amount) if amount else 0}
        for hour, count, amount in hourly_sales
    ]

    return {
        "date": start_date.date().isoformat(),
        "order_count": order_count,
        "total_sales": total_sales,
        "avg_order_amount": avg_order_amount,
        "payment_methods": payment_breakdown,
        "hourly_sales": hourly_breakdown,
    }


def get_popular_items(
    db: Session, start_date: datetime, end_date: datetime, limit: int = 10
) -> List[Dict[str, Any]]:
    """獲取熱門商品報表"""
    popular_items = db.execute(
        select(
            MenuItem.uuid,
            MenuItem.name,
            MenuItem.category,
            MenuItem.price,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.subtotal).label("total_sales"),
        )
        .join(OrderItem, MenuItem.uuid == OrderItem.item_uuid)
        .join(Order, OrderItem.order_uuid == Order.uuid)
        .where(
            Order.create_dt >= start_date,
            Order.create_dt < end_date,
            Order.status == "completed",
            Order.soft_delete == False,
            OrderItem.soft_delete == False,
            MenuItem.soft_delete == False,
        )
        .group_by(MenuItem.uuid, MenuItem.name, MenuItem.category, MenuItem.price)
        .order_by(desc(text("total_quantity")))
        .limit(limit)
    ).all()

    return [
        {
            "uuid": str(uuid),
            "name": name,
            "category": category,
            "price": float(price),
            "total_quantity": total_quantity,
            "total_sales": float(total_sales) if total_sales else 0,
            "percentage_of_sales": None,  # 將在後續計算
        }
        for uuid, name, category, price, total_quantity, total_sales in popular_items
    ]


def get_inventory_status(db: Session) -> Dict[str, Any]:
    """獲取庫存狀態報表"""
    inventory_query = (
        select(
            MenuItem.uuid,
            MenuItem.name,
            MenuItem.category,
            MenuItem.stock_quantity,
            MenuItem.available,
        )
        .where(MenuItem.soft_delete == False)
        .order_by(MenuItem.stock_quantity)
    )

    inventory_items = db.execute(inventory_query).all()

    # 分類庫存狀態
    low_inventory = []
    out_of_stock = []
    healthy_inventory = []

    for uuid, name, category, stock, available in inventory_items:
        item_data = {
            "uuid": str(uuid),
            "name": name,
            "category": category,
            "stock_quantity": stock or 0,
            "available": available,
        }

        if stock is None or stock <= 0:
            out_of_stock.append(item_data)
        elif stock < 10:  # 定義低庫存閾值
            low_inventory.append(item_data)
        else:
            healthy_inventory.append(item_data)

    return {
        "out_of_stock_count": len(out_of_stock),
        "low_inventory_count": len(low_inventory),
        "healthy_inventory_count": len(healthy_inventory),
        "out_of_stock": out_of_stock,
        "low_inventory": low_inventory,
        "healthy_inventory": healthy_inventory,
    }
