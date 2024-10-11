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
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false

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
            if get_user(db, username) is not None:
                raise HTTPException(status_code=400, detail="username already exist")
            create_user = User(user_status=user_status, username=username)
        case 1:
            if desk_number == "" or username is None:
                raise HTTPException(status_code=400, detail="desk_number error")
            if get_user_by_desk_number(db, desk_number) is not None:
                raise HTTPException(status_code=400, detail="desk_number already exist")
            create_user = User(user_status=user_status, desk_number=desk_number)
        case _:
            raise HTTPException(status_code=400, detail="user_status error")
    create_user.password(password)
    db.add(create_user)
    db.commit(create_user)
    db.refresh(create_user)
    return create_user


def get_user(db: Session, user_name: UUID):
    return db.execute(
        select(User).where(
            User.username == user_name,
            User.user_status == 0,
            User.soft_delete == false(),
        )
    ).scalar()


def get_user_by_desk_number(db: Session, desk_number: str):
    return db.execute(
        select(User).where(
            User.desk_number == desk_number,
            User.user_status == 1,
            User.soft_delete == false(),
        )
    ).scalar()


def get_user_by_uuid(db: Session, user_uuid: UUID):
    return db.execute(
        select(User).where(User.uuid == user_uuid, User.soft_delete == false())
    ).scalar()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    """return total and list"""
    users = (
        db.execute(
            select(User).where(User.soft_delete == false()).offset(skip).limit(limit)
        )
        .scalars()
        .all()
    )
    total = db.execute(
        select(func.count(User.id)).where(User.soft_delete == false())
    ).scalars()
    return {"total": total, "skip": skip, "limit": limit, "users": users}
