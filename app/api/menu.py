from fastapi import Depends, HTTPException, status
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
import logging

log = logging.getLogger(__name__)


@app.post("/menu/items/", response_model=MenuItemResponse)
async def add_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # 只有員工可以創建菜單項目
    if hasattr(current_user, "user_status") and current_user.user_status in [
        2,
        3,
    ]:  # Customer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can manage menu items",
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
    """獲取包含庫存信息的菜單項目"""
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
    current_user=Depends(get_current_user),
):
    # 只有員工可以修改菜單項目
    if hasattr(current_user, "user_status") and current_user.user_status in [
        2,
        3,
    ]:  # Customer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can manage menu items",
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
async def remove_menu_item(item_uuid: str, db: Session = Depends(get_session)):
    try:
        result = delete_menu_item(db=db, item_uuid=item_uuid)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
