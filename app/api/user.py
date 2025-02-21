import logging
from typing import List, Optional,Dict
from pydantic import Json
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from fastapi import Depends
from app.extension.sql_ext import get_session
from fastapi.responses import JSONResponse
from app import app
from app.adapter import body_schema, sql_crud
from app.handler.vaild import errmsn
from sqlalchemy.orm import Session
from app.extension.jwt_config import get_current_user
from app.adapter.sql_adapter import User
log = logging.getLogger(__name__)


@app.post("/creat_user/", response_model=body_schema.UserData)
def creat_user(
    db: Session = Depends(get_session),
    current_user: body_schema.UserData = Depends(get_current_user),
    user_status: int = 0,
    username: str = None,
    desk_number: str = None,
    password: str = None,
    email: Optional[str] = None,
    gender: Optional[int] = None,
    true_name: Optional[str] = None,
    info: Optional[Dict] = None
):

    try:
        user = sql_crud.create_user(
            user_status=user_status,
            username=username,
            desk_number=desk_number,
            password=password,
            email=email,
            gender=gender,
            ture_name=true_name,
            info=info ,
            db=db,
        )
        return user

    except Exception as e:
        log.critical(e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )


@app.get("/get_current_user/", response_model=body_schema.UserData)
def get_users(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.get("/get_user_by_uuid/", response_model=body_schema.UserData)
def get_user_by_uuid(
    db: Session = Depends(get_session),
    current_user: body_schema.UserData = Depends(get_current_user),
    user_uuid: str = None,
):
    return sql_crud.get_user_by_uuid(user_uuid=user_uuid, db=db)
