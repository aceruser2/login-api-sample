from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.model import Order, OrderItem, MenuItem
from app.schema import DailySalesReport, PopularItemReport
from typing import Dict, Any


def get_daily_sales(db: Session, date: datetime):
    """產生日銷售報表"""
    start_date = date.replace(hour=0, minute=0, second=0)
    end_date = start_date + timedelta(days=1)

    stmt = select(
        func.count(Order.uuid).label("total_orders"),
        func.sum(Order.total_amount).label("total_sales"),
    ).where(
        Order.create_dt >= start_date,
        Order.create_dt < end_date,
        Order.status == 2,  # completed
        Order.soft_delete == False,
    )

    result = db.execute(stmt).first()

    return DailySalesReport(
        date=date,
        total_sales=result.total_sales or 0,
        total_orders=result.total_orders or 0,
        average_order_value=(
            result.total_sales / result.total_orders if result.total_orders else 0
        ),
    )


def get_popular_items(
    db: Session, start_date: datetime, end_date: datetime, limit: int = 10
):
    """獲取熱門商品統計"""
    stmt = (
        select(
            MenuItem.uuid,
            MenuItem.name,
            func.sum(OrderItem.quantity).label("quantity_sold"),
            func.sum(OrderItem.subtotal).label("total_sales"),
        )
        .join(OrderItem, OrderItem.item_uuid == MenuItem.uuid)
        .join(Order, Order.uuid == OrderItem.order_uuid)
        .where(
            Order.create_dt >= start_date,
            Order.create_dt < end_date,
            Order.status == 2,  # completed
            Order.soft_delete == False,
        )
        .group_by(MenuItem.uuid, MenuItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )

    results = db.execute(stmt).all()

    return [
        PopularItemReport(
            item_uuid=r.uuid,
            item_name=r.name,
            quantity_sold=r.quantity_sold,
            total_sales=r.total_sales,
        )
        for r in results
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
