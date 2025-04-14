from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import app
from app.adapter.menu import (
    create_menu_item,
    get_menu_items,
    update_menu_item,
    delete_menu_item,
    get_menu_item_by_uuid,
)
from app.extension.sql_ext import get_session
from app.adapter.schema import MenuItemCreate, MenuItemUpdate, MenuItemResponse


@app.post("/menu/items/", response_model=MenuItemResponse)
async def add_menu_item(item: MenuItemCreate, db: Session = Depends(get_session)):
    return create_menu_item(db=db, item=item)


@app.get("/menu/items/", response_model=list[MenuItemResponse])
async def list_menu_items(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    db: Session = Depends(get_session),
):
    return get_menu_items(db=db, skip=skip, limit=limit, category=category)


@app.put("/menu/items/{item_uuid}", response_model=MenuItemResponse)
async def modify_menu_item(
    item_uuid: str, item: MenuItemUpdate, db: Session = Depends(get_session)
):
    return update_menu_item(db=db, item_uuid=item_uuid, item=item)


@app.delete("/menu/items/{item_uuid}")
async def remove_menu_item(item_uuid: str, db: Session = Depends(get_session)):
    return delete_menu_item(db=db, item_uuid=item_uuid)
