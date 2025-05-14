import logging
from typing import List, Optional, Dict
from pydantic import Json
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException
from app.extension.sql_ext import get_session
from fastapi.responses import JSONResponse
from app import app
from app.adapter import schema, user
from app.handler.vaild import errmsn
from sqlalchemy.orm import Session
from app.extension.jwt_config import get_current_user
from app.adapter.model import User

log = logging.getLogger(__name__)


@app.get("/get_current_user/", response_model=schema.UserData)
def get_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.get("/get_user_by_uuid/", response_model=schema.UserData)
def get_user_by_uuid(
    db: Session = Depends(get_session),
    current_user: schema.UserData = Depends(get_current_user),
    user_uuid: str = None,
):
    return user.get_user_by_uuid(user_uuid=user_uuid, db=db)


@app.delete("/delete_user/", response_model=schema.UserData)
def delete_user(
    db: Session = Depends(get_session),
    current_user: schema.UserData = Depends(get_current_user),
    user_uuid: str = None,
):
    """刪除使用者"""
    try:
        return user.delete_user(db=db, user_uuid=user_uuid)
    except Exception as e:
        log.critical(e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )


@app.post("/creat_user/", response_model=schema.UserData)
def create_user(
    db: Session = Depends(get_session),
    current_user: schema.UserData = Depends(get_current_user),
    user_status: int = 0,
    username: str = None,
    desk_number: str = None,
    password: str = None,
    email: Optional[str] = None,
    gender: Optional[int] = None,
    true_name: Optional[str] = None,
    info: Optional[Dict] = None,
):
    if not username or not password:
        return JSONResponse(
            status_code=400, content={"message": "Username and password are required"}
        )

    try:
        user = user.create_user(
            username=username,
            password=password,
            email=email,
            gender=gender,
            true_name=true_name,
            db=db,
        )
        return user
    except Exception as e:
        log.critical(e, exc_info=True)
        return JSONResponse(status_code=500, content={"message": str(e)})
