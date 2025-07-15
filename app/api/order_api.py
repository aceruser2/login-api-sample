from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import app
from app.services.order_service import (
    create_order,
    get_orders,
    update_order_status,
    get_order_by_uuid,
    get_orders_by_customer,
    update_order,
)
from app.extension.sql_ext import get_session
from app.schema import OrderCreate, OrderResponse, OrderUpdate, OrderStatusUpdate
from app.extension.jwt_config import get_current_user
from app.utils.permission_utils import (
    get_user_info_from_token,
    can_create_order,
    can_view_order,
    can_update_order,
    can_update_order_status,
    filter_orders_by_permission,
)
import logging

log = logging.getLogger(__name__)


@app.post("/orders/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """創建新訂單"""
    try:
        user_info = get_user_info_from_token(current_user)

        # 檢查創建訂單權限
        if not can_create_order(user_info, order.customer_uuid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create orders for yourself",
            )

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
    status_filter: str = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """獲取訂單列表"""
    try:
        user_info = get_user_info_from_token(current_user)

        # 根據用戶類型獲取訂單
        if user_info["user_type"] == "customer":
            orders = get_orders_by_customer(
                db=db, customer_uuid=user_info["uuid"], skip=skip, limit=limit
            )
        else:
            orders = get_orders(db=db, skip=skip, limit=limit, status=status_filter)

        # 根據權限過濾訂單
        filtered_orders = filter_orders_by_permission(user_info, orders)
        return filtered_orders
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/orders/{order_uuid}", response_model=OrderResponse)
async def update_order_content(
    order_uuid: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """更新訂單內容（僅pending狀態）"""
    try:
        user_info = get_user_info_from_token(current_user)

        # 獲取訂單
        order = get_order_by_uuid(db=db, order_uuid=order_uuid)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # 檢查更新權限
        if not can_update_order(user_info, order.customer_uuid, order.status):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own pending orders",
            )

        updated_order = update_order(
            db=db, order_uuid=order_uuid, order_update=order_update
        )
        db.commit()
        return updated_order
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/orders/{order_uuid}/status", response_model=OrderResponse)
async def update_order_status_endpoint(
    order_uuid: str,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """更新訂單狀態（僅員工）"""
    try:
        user_info = get_user_info_from_token(current_user)

        # 檢查狀態更新權限
        if not can_update_order_status(user_info):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff can update order status",
            )

        result = update_order_status(
            db=db, order_uuid=order_uuid, status=status_update.status
        )
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/{order_uuid}", response_model=OrderResponse)
async def get_order(
    order_uuid: str,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """獲取特定訂單"""
    try:
        user_info = get_user_info_from_token(current_user)

        order = get_order_by_uuid(db=db, order_uuid=order_uuid)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # 檢查查看權限
        if not can_view_order(user_info, order.customer_uuid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only access your own orders",
            )

        return order
    except HTTPException:
        raise
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
