from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app import app
from app.services.user_service import (
    get_user_all_role_and_permission,
    create_user,
    delete_user,
    get_user_by_uuid,
)
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.schema import UserData
import logging

log = logging.getLogger(__name__)


@app.get("/users/me")
async def get_current_user_info(
    current_user=Depends(get_current_user), db: Session = Depends(get_session)
):
    """獲取當前用戶信息"""
    try:
        user = get_user_by_uuid(db, current_user.uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_uuid}")
async def get_user_info(
    user_uuid: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """獲取指定用戶信息"""
    try:
        user = get_user_by_uuid(db, user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))





@app.delete("/delete_user/", response_model=UserData)
async def delete_user_api(
    user_uuid: str,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """刪除使用者（軟刪除）"""
    try:
        result = delete_user(db=db, user_uuid=user_uuid)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/create_user/", response_model=UserData)
async def create_user_api(
    username: str,
    password: str,
    email: Optional[str] = None,
    gender: Optional[str] = None,
    true_name: Optional[str] = None,
    role_uuid: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """創建新使用者"""
    if not username or not password:
        raise HTTPException(
            status_code=400, detail="Username and password are required"
        )
    try:
        user = create_user(
            db=db,
            username=username,
            password=password,
            email=email,
            gender=gender,
            true_name=true_name,
            role_uuid=role_uuid,
        )
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
