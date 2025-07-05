from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import app
from app.services.order_service import (
    create_order,
    get_orders,
    update_order_status,
    get_order_by_uuid,
)
from app.extension.sql_ext import get_session
from app.schema import OrderCreate, OrderResponse
from app.extension.jwt_config import get_current_user
import logging

log = logging.getLogger(__name__)


@app.post("/orders/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # 顧客只能為自己創建訂單
    if hasattr(current_user, "user_status") and current_user.user_status in [
        2,
        3,
    ]:  # Customer
        if order.customer_uuid != current_user.uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create orders for yourself",
            )
    # 員工可以為任何顧客創建訂單
    try:
        order_obj = create_order(db=db, order=order)
        db.commit()
        return order_obj
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        orders = get_orders(db=db, skip=skip, limit=limit, status=status)
        # 如果是顧客，只能看到自己的訂單
        if hasattr(current_user, "user_status") and current_user.user_status in [2, 3]:
            orders = [o for o in orders if o.customer_uuid == current_user.uuid]
        return orders
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/orders/{order_uuid}/status")
async def update_order(
    order_uuid: str,
    status: str,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # 只有員工可以更新訂單狀態
    if hasattr(current_user, "user_status") and current_user.user_status in [
        2,
        3,
    ]:  # Customer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update order status",
        )
    try:
        result = update_order_status(db=db, order_uuid=order_uuid, status=status)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
