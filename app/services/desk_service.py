import logging
from uuid import UUID
from sqlalchemy.sql.expression import false
from app.model import Desk
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from sqlalchemy import func

log = logging.getLogger(__name__)


def create_desk(db: Session, desk_name: str):
    """建立桌子"""
    create_desk = Desk(desk_name=desk_name)
    db.add(create_desk)
    return create_desk


def get_desk_by_uuid(db: Session, desk_uuid: str):
    """取得桌子"""
    desk = select(Desk).where(Desk.uuid == desk_uuid, Desk.soft_delete == false())
    return db.execute(desk).scalar()


def get_all_desks(db: Session, skip: int = 0, limit: int = 10):
    """取得所有桌子"""
    desks = select(Desk).where(Desk.soft_delete == false()).offset(skip).limit(limit)
    total = select(func.count(Desk.uuid)).where(Desk.soft_delete == false())
    return {
        "total": db.execute(total).scalar(),
        "skip": skip,
        "limit": limit,
        "desks": db.execute(desks).scalars().all(),
    }


def update_desk(db: Session, desk_uuid: str, desk_name: str):
    """更新桌子"""
    desk = get_desk_by_uuid(db, desk_uuid)
    if desk is None:
        raise ValueError("desk not found")
    desk.desk_name = desk_name
    return desk


def delete_desk(db: Session, desk_uuid: str):
    """刪除桌子"""
    desk = get_desk_by_uuid(db, desk_uuid)
    if desk is None:
        raise ValueError("desk not found")
    desk.soft_delete = True
    return desk
