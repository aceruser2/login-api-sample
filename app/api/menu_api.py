from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import app
from app.services.menu_service import (
    create_menu_item,
    get_menu_items,
    update_menu_item,
    delete_menu_item,
    get_menu_items_with_inventory,
)
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.schema import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
    MenuItemWithInventoryResponse,
)
from app.utils.permission_checker import PermissionChecker
import logging
from typing import Tuple

log = logging.getLogger(__name__)


@app.post("/menu/items/", response_model=MenuItemResponse)
async def add_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """新增菜單項目（需要菜單管理創建權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "menu_management", "can_create"
    )
    try:
        menu_item = create_menu_item(db=db, item=item)
        db.commit()
        return menu_item
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/menu/items/", response_model=list[MenuItemResponse])
async def list_menu_items(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    db: Session = Depends(get_session),
):
    """獲取菜單項目列表（公開）"""
    try:
        return get_menu_items(db=db, skip=skip, limit=limit, category=category)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/menu/items-with-inventory/", response_model=list[MenuItemWithInventoryResponse]
)
async def get_menu_items_with_inventory_api(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    db: Session = Depends(get_session),
):
    """獲取包含庫存信息的菜單項目（公開）"""
    try:
        return get_menu_items_with_inventory(
            db=db, skip=skip, limit=limit, category=category
        )
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/menu/items/{item_uuid}", response_model=MenuItemResponse)
async def modify_menu_item(
    item_uuid: str,
    item: MenuItemUpdate,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """修改菜單項目（需要菜單管理更新權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "menu_management", "can_update"
    )
    try:
        updated_item = update_menu_item(db=db, item_uuid=item_uuid, item=item)
        db.commit()
        return updated_item
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/menu/items/{item_uuid}")
async def remove_menu_item(
    item_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """刪除菜單項目（需要菜單管理刪除權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "menu_management", "can_delete"
    )
    try:
        result = delete_menu_item(db=db, item_uuid=item_uuid)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
