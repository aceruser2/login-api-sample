import logging
from uuid import UUID
from sqlalchemy.sql.expression import false
from app.model.desk_model import Desk
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schema.desk_schema import CreateDeskSchema, UpdateDeskSchema

log = logging.getLogger(__name__)


def create_desk(db: Session, desk_data: CreateDeskSchema) -> Desk:
    """創建桌位"""
    # 檢查桌位名稱是否已存在
    existing_desk = get_desk_by_name(db, desk_data.desk_name)
    if existing_desk:
        raise ValueError(f"Desk with name '{desk_data.desk_name}' already exists")

    new_desk = Desk(
        desk_name=desk_data.desk_name,
        capacity=desk_data.capacity,
        is_available=desk_data.is_available,
    )
    db.add(new_desk)
    db.flush()
    return new_desk


def get_desk_by_uuid(db: Session, desk_uuid: str) -> Optional[Desk]:
    """根據UUID獲取桌位"""
    stmt = select(Desk).where(Desk.uuid == desk_uuid, Desk.soft_delete == False)
    return db.execute(stmt).scalar_one_or_none()


def get_all_desks(db: Session, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """獲取所有桌位"""
    # 獲取總數
    count_stmt = select(func.count(Desk.uuid)).where(Desk.soft_delete == False)
    total = db.execute(count_stmt).scalar()

    # 獲取桌位列表
    stmt = select(Desk).where(Desk.soft_delete == False).offset(skip).limit(limit)
    desks = db.execute(stmt).scalars().all()

    return {"total": total, "desks": desks, "skip": skip, "limit": limit}


def update_desk(db: Session, desk_uuid: str, desk_data: UpdateDeskSchema) -> Desk:
    """更新桌位"""
    desk = get_desk_by_uuid(db, desk_uuid)
    if not desk:
        raise ValueError("Desk not found")

    # 檢查名稱是否與其他桌位衝突
    if desk_data.desk_name and desk_data.desk_name != desk.desk_name:
        existing_desk = get_desk_by_name(db, desk_data.desk_name)
        if existing_desk and existing_desk.uuid != desk_uuid:
            raise ValueError(f"Desk with name '{desk_data.desk_name}' already exists")

    for field, value in desk_data.dict(exclude_unset=True).items():
        setattr(desk, field, value)

    db.flush()
    return desk


def delete_desk(db: Session, desk_uuid: str) -> Desk:
    """軟刪除桌位"""
    desk = get_desk_by_uuid(db, desk_uuid)
    if not desk:
        raise ValueError("Desk not found")

    desk.soft_delete = True
    db.flush()
    return desk


def get_desk_by_name(db: Session, desk_name: str) -> Optional[Desk]:
    """根據名稱獲取桌位"""
    stmt = select(Desk).where(Desk.desk_name == desk_name, Desk.soft_delete == False)
    return db.execute(stmt).scalar_one_or_none()


def get_available_desks(db: Session) -> List[Desk]:
    """獲取可用桌位"""
    stmt = select(Desk).where(Desk.is_available == True, Desk.soft_delete == False)
    return db.execute(stmt).scalars().all()
