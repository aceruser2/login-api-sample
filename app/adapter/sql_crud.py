"""
[sql邏輯crud]
 
"""

import logging
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.sql.expression import false
from app.adapter.sql_adapter import User
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


def create_user(
    db: Session, user_status: int, username: str, desk_number: str, password: str
):
    """用sqlalchemy建立使用者的函式
    0:員工用,1:內用
    """
    create_user = None
    match user_status:
        case 0:
            if username == "" or username is None:
                raise HTTPException(status_code=400, detail="username error")
            create_user = User(user_status=user_status, username=username)
        case 1:
            if desk_number == "" or username is None:
                raise HTTPException(status_code=400, detail="desk_number error")
            create_user = User(user_status=user_status, desk_number=desk_number)
        case _:
            raise HTTPException(status_code=400, detail="user_status error")
    create_user.password(password)
    db.add(create_user)
    db.commit(create_user)
    db.refresh(create_user)
    return create_user


def get_user(db: Session, user_name: UUID):
    return db.execute(select(User).where(User.username == user_name)).scalar()
