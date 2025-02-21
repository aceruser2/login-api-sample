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
from sqlalchemy import func
from app.extension.emun_setting import UserStatusEmun

log = logging.getLogger(__name__)


def create_user(
    db: Session,
    user_status: int,
    username: str,
    desk_number: str,
    password: str,
    email: str = None,
    gender: str = None,
    ture_name: str = None,
):
    """用sqlalchemy建立使用者的函式
    0:員工用,1:內用
    """
    create_user = None

    match user_status:
        case UserStatusEmun.STAFF.value:
            if username == "" or username is None:
                raise HTTPException(status_code=400, detail="username error")
            if get_user_by_username(db, username) is not None:
                raise HTTPException(status_code=400, detail="username already exist")
            info_data = {"gender": gender, "true_name": ture_name}
            create_user = User(
                user_status=user_status, username=username, email=email, info=info_data
            )
        case UserStatusEmun.DESK.value:
            if desk_number == "" or username is None:
                raise HTTPException(status_code=400, detail="desk_number error")
            if get_user_by_desk(db, desk_number) is not None:
                raise HTTPException(status_code=400, detail="desk_number already exist")
            create_user = User(user_status=user_status, desk_number=desk_number)

        case _:
            raise HTTPException(status_code=400, detail="user_status error")
    create_user.password(password)
    db.add(create_user)
    db.commit(create_user)
    db.refresh(create_user)
    return create_user


def get_user_by_username(db: Session, user_name: str)->User:
    return db.execute(
        select(User).where(
            User.username == user_name,
            User.user_status == UserStatusEmun.STAFF.value,
            User.soft_delete == false(),
        )
    ).scalar()


def get_user_by_desk(db: Session, desk_number: str)->User:
    return db.execute(
        select(User).where(
            User.desk_number == desk_number,
            User.user_status == UserStatusEmun.DESK.value,
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


def update_user(
    db: Session, user_uuid: UUID, user_status: int, username: str, desk_number: str
):
    """update user"""

    update_user = get_user_by_uuid(db, user_uuid)
    if update_user is None:
        raise HTTPException(status_code=400, detail="user not found")
    update_user.user_status = user_status
    update_user.username = username
    update_user.desk_number = desk_number
    db.commit()
    db.flush()
    return update_user


def delete_user(db: Session, user_uuid: UUID):
    """delete user"""
    delete_user = get_user_by_uuid(db, user_uuid)
    if delete_user is None:
        raise HTTPException(status_code=400, detail="user not found")
    delete_user.soft_delete = True
    db.commit()
    db.flush()
    return delete_user
