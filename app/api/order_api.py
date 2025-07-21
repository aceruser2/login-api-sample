from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Tuple
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
from app.extension.emun_setting import OrderStatusEnum
from app.utils.permission_checker import PermissionChecker
import logging

log = logging.getLogger(__name__)


@app.post("/orders/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """創建新訂單"""
    user_object, user_type = user_data
    user_uuid = user_object.uuid

    # 員工需要訂單管理創建權限，顧客只能為自己創建訂單
    if user_type == "staff":
        PermissionChecker.require_staff_with_permission(
            user_data, db, "order_management", "can_create"
        )
    elif user_type == "customer" and order.customer_uuid != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customers can only create orders for themselves.",
        )

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
    status_filter: int = None,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取訂單列表"""
    user_object, user_type = user_data
    user_uuid = user_object.uuid

    try:
        if user_type == "staff":
            # 員工需要訂單管理讀取權限
            PermissionChecker.require_staff_with_permission(
                user_data, db, "order_management", "can_read"
            )
            return get_orders(db=db, skip=skip, limit=limit, status=status_filter)
        elif user_type == "customer":
            # 顧客只能查看自己的訂單
            return get_orders_by_customer(
                db=db, customer_uuid=user_uuid, skip=skip, limit=limit
            )
        else:
            return []
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/orders/{order_uuid}", response_model=OrderResponse)
async def update_order_content(
    order_uuid: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """更新訂單內容"""
    user_object, user_type = user_data
    user_uuid = user_object.uuid

    order = get_order_by_uuid(db=db, order_uuid=order_uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 權限檢查
    can_update = False
    if user_type == "staff":
        # 員工需要訂單管理更新權限
        PermissionChecker.require_staff_with_permission(
            user_data, db, "order_management", "can_update"
        )
        can_update = True
    elif user_type == "customer":
        # 顧客只能更新自己的pending訂單
        is_own_order = order.customer_uuid == user_uuid
        is_pending = order.status == OrderStatusEnum.PENDING.value
        if is_own_order and is_pending:
            can_update = True

    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Can only update your own pending orders.",
        )

    try:
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
    user_data: Tuple = Depends(get_current_user),
):
    """更新訂單狀態（需要訂單狀態管理權限）"""
    user_object, user_type = user_data

    # 只有員工可以更新訂單狀態
    if user_type != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update order status.",
        )

    # 檢查訂單狀態管理權限
    PermissionChecker.require_staff_with_permission(
        user_data, db, "order_status_management", "can_update"
    )

    try:
        # 將傳入的狀態字串轉換為對應的 Enum 成員，再取其值
        if hasattr(status_update.status, "value"):
            # 如果是 Enum 對象
            status_value = status_update.status.value
        else:
            # 如果是字串，嘗試轉換為 Enum
            status_value = OrderStatusEnum[status_update.status.upper()].value

        result = update_order_status(db=db, order_uuid=order_uuid, status=status_value)
        db.commit()
        return result
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status provided: {status_update.status}",
        )
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/{order_uuid}", response_model=OrderResponse)
async def get_order(
    order_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取特定訂單"""
    user_object, user_type = user_data
    user_uuid = user_object.uuid

    order = get_order_by_uuid(db=db, order_uuid=order_uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 權限檢查
    if user_type == "staff":
        # 員工需要訂單管理讀取權限
        PermissionChecker.require_staff_with_permission(
            user_data, db, "order_management", "can_read"
        )
        return order
    elif user_type == "customer" and order.customer_uuid == user_uuid:
        # 顧客只能查看自己的訂單
        return order
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this order.",
        )
