from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import app
from app.adapter.order import (
    create_order,
    get_orders,
    update_order_status,
    get_order_by_uuid,
)
from app.extension.sql_ext import get_session
from app.adapter.schema import OrderCreate, OrderUpdate, OrderResponse
from app.extension.jwt_config import get_current_user


@app.post("/orders/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # Verify customer placing order matches authenticated user
    if order.customer_uuid != current_user.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create orders for yourself",
        )
    return create_order(db=db, order=order)


@app.get("/orders/", response_model=list[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # Staff can see all orders, customers only see their own
    orders = get_orders(db=db, skip=skip, limit=limit, status=status)
    if current_user.user_status in [2, 3]:  # Customer or delivery
        orders = [o for o in orders if o.customer_uuid == current_user.uuid]
    return orders


@app.put("/orders/{order_uuid}/status")
async def update_order(
    order_uuid: str,
    status: str,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # Only staff can update order status
    if current_user.user_status in [2, 3]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update order status",
        )
    return update_order_status(db=db, order_uuid=order_uuid, status=status)
