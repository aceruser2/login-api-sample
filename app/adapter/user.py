"""
[sql邏輯crud]

"""

import logging
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.sql.expression import false
from app.adapter.model import User, RoleUser, Role, Permission, RolePermission
from sqlalchemy import select, insert, or_
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.adapter.schema import LoginData

log = logging.getLogger(__name__)


def create_role(db: Session, role_name: str, level: int):
    """建立角色"""

    new_role = Role(role_name=role_name, level=level)
    db.add(new_role)
    db.flush()
    return new_role


def create_permission(db: Session, permission_name: str, permission_attributes: dict):
    """建立權限"""

    new_permission = Permission(
        permission_name=permission_name, permission_attributes=permission_attributes
    )
    db.add(new_permission)
    db.flush()
    return new_permission


def create_role_permission(db: Session, role_uuid: int, permission_uuid: int):
    """建立角色權限"""

    new_role_permission = RolePermission(
        role_uuid=role_uuid, permission_uuid=permission_uuid
    )
    db.add(new_role_permission)
    db.flush()
    return new_role_permission


def get_role_and_permission_by_role_uuid(db: Session, role_uuid: str):
    """取得角色權限"""
    try:
        role = (
            select(Role)
            .join(RolePermission, Role.uuid == RolePermission.role_uuid)
            .join(Permission, Permission.uuid == RolePermission.permission_uuid)
            .where(
                Role.uuid == role_uuid,
                Role.soft_delete == false(),
                Permission.soft_delete == false(),
                RolePermission.soft_delete == false(),
            )
        )
        return db.execute(role).scalar()

    except Exception as e:
        log.error(e, exc_info=True)
        raise e


def get_user_all_role_and_permission(
    db: Session, user_uuid: str, skip: int = 0, limit: int = 10
):
    """取得使用者所有角色權限list"""
    try:

        user = (
            select(User)
            .join(
                RoleUser,
                User.uuid == RoleUser.user_uuid,
                isouter=True,  # 只保留join條件
            )
            .join(Role, Role.uuid == RoleUser.role_uuid, isouter=True)
            .join(RolePermission, Role.uuid == RolePermission.role_uuid, isouter=True)
            .join(
                Permission,
                Permission.uuid == RolePermission.permission_uuid,
                isouter=True,
            )
            .where(
                User.soft_delete == false(),
                or_(RoleUser.soft_delete == false(), RoleUser.uuid == None),
                or_(Role.soft_delete == false(), Role.uuid == None),
                or_(RolePermission.soft_delete == false(), RolePermission.uuid == None),
                or_(Permission.soft_delete == false(), Permission.uuid == None),
            )
            .offset(skip)
            .limit(limit)
        )

        total = (
            select(User)
            .join(
                RoleUser,
                User.uuid == RoleUser.user_uuid,
                isouter=True,  # 只保留join條件
            )
            .join(Role, Role.uuid == RoleUser.role_uuid, isouter=True)
            .join(RolePermission, Role.uuid == RolePermission.role_uuid, isouter=True)
            .join(
                Permission,
                Permission.uuid == RolePermission.permission_uuid,
                isouter=True,
            )
            .where(
                User.soft_delete == false(),
                or_(RoleUser.soft_delete == false(), RoleUser.uuid == None),
                or_(Role.soft_delete == false(), Role.uuid == None),
                or_(RolePermission.soft_delete == false(), RolePermission.uuid == None),
                or_(Permission.soft_delete == false(), Permission.uuid == None),
            )
        )
        return {
            "total": db.execute(total).scalar(),
            "skip": skip,
            "limit": limit,
            "users": db.execute(user).scalars().all(),
        }
    except Exception as e:
        log.error(e, exc_info=True)
        raise e


def get_user_all_role_and_permission_by_user_uuid(db: Session, user_uuid: str):
    """取得使用者所有角色權限"""
    try:
        user = (
            select(User, Role, Permission)
            .join(
                RoleUser,
                User.uuid == RoleUser.user_uuid,
                isouter=True,  # 只保留join條件
            )
            .join(Role, Role.uuid == RoleUser.role_uuid, isouter=True)
            .join(RolePermission, Role.uuid == RolePermission.role_uuid, isouter=True)
            .join(
                Permission,
                Permission.uuid == RolePermission.permission_uuid,
                isouter=True,
            )
            .where(
                User.uuid == user_uuid,
                User.soft_delete == false(),
                or_(RoleUser.soft_delete == false(), RoleUser.id == None),
                or_(Role.soft_delete == false(), Role.uuid == None),
                or_(RolePermission.soft_delete == false(), RolePermission.id == None),
                or_(Permission.soft_delete == false(), Permission.uuid == None),
            )
        )

        return db.execute(user).all()  # 回傳所有權限

    except Exception as e:
        log.error(e, exc_info=True)
        raise e


def get_user_by_username(db: Session, username: str):
    """取得使用者"""
    try:
        user = select(User).where(
            User.username == username, User.soft_delete == false()
        )
        return db.execute(user).scalar()
    except Exception as e:
        log.error(e, exc_info=True)
        raise e


def create_user(
    db: Session,
    username: str,
    password: str,
    email: str = None,
    gender: str = None,
    true_name: str = None,
    role_uuid: int = None,
):
    """用sqlalchemy建立使用者的函式
    員工用
    """
    try:
        role = None
        if role_uuid:
            role = get_role_and_permission_by_role_uuid(db, role_uuid)
            if role is None:
                raise HTTPException(status_code=400, detail="role not found")
        if username == "" or username is None:
            raise HTTPException(status_code=400, detail="username error")
        if get_user_by_username(db, username) is not None:
            raise HTTPException(status_code=400, detail="username already exist")
        info_data = {"gender": gender, "true_name": true_name}
        new_user = User(username=username, email=email, info=info_data)
        new_user.password = password
        db.add(new_user)
        db.flush()  # 先 flush 讓 create_user.uuid 產生
        if role_uuid:
            role_user = RoleUser(user_uuid=new_user.uuid, role_uuid=role_uuid)
            db.add(role_user)
            db.flush()
        return new_user
    except Exception as e:
        log.error(e, exc_info=True)
        raise e


def get_user_by_uuid(db: Session, user_uuid: str):
    """取得使用者"""
    try:
        user = select(User).where(User.uuid == user_uuid, User.soft_delete == false())
        return db.execute(user).scalar()
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get user error")


def get_role_user_by_user_uuid(db: Session, user_uuid: str):
    """取得使用者角色"""
    try:
        role_user = select(RoleUser).where(
            RoleUser.user_uuid == user_uuid, RoleUser.soft_delete == false()
        )
        return db.execute(role_user).scalars().all()
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get role user error")


def delete_user(db: Session, user_uuid: str):
    """delete user"""
    try:
        if user_uuid is None:
            raise HTTPException(status_code=400, detail="user_uuid is None")

        for i in get_role_user_by_user_uuid(db, user_uuid):
            i.soft_delete = True

        delete_user = get_user_by_uuid(db, user_uuid)
        if delete_user is None:
            raise HTTPException(status_code=400, detail="user not found")
        delete_user.soft_delete = True
        db.commit()
        db.flush()
        return delete_user
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="delete user error")
