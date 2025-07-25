from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.extension.sql_ext import get_session
from app.services import desk_service
from app.schema.desk_schema import (
    CreateDeskSchema,
    UpdateDeskSchema,
    DeskOutSchema,
    DeskQRCodeResponse,
)
from app.extension.jwt_config import get_current_user
from app.utils.permission_checker import PermissionChecker
from typing import List, Tuple
import logging

router = APIRouter(prefix="/desks", tags=["desks"])
log = logging.getLogger(__name__)


@router.post("/", response_model=DeskOutSchema, status_code=status.HTTP_201_CREATED)
def create_desk(
    desk_data: CreateDeskSchema,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """創建新桌位（需要桌位管理創建權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "desk_management", "can_create"
    )
    try:
        desk = desk_service.create_desk(db, desk_data.desk_name)
        db.commit()
        return desk
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[DeskOutSchema])
def get_all_desks(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """獲取所有桌位（公開）"""
    try:
        desks = desk_service.get_all_desks(db, skip=skip, limit=limit)
        return desks
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{desk_uuid}", response_model=DeskOutSchema)
def get_desk_endpoint(
    desk_uuid: str,
    db: Session = Depends(get_session),
):
    """獲取單個桌位（公開）"""
    try:
        desk = desk_service.get_desk_by_uuid(db, desk_uuid)
        if not desk:
            raise HTTPException(status_code=404, detail="Desk not found")
        return desk
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{desk_uuid}", response_model=DeskOutSchema)
def update_desk(
    desk_uuid: str,
    desk_data: UpdateDeskSchema,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """更新桌位（需要桌位管理更新權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "desk_management", "can_update"
    )
    try:
        desk = desk_service.update_desk(db, desk_uuid, desk_data.desk_name)
        if not desk:
            raise HTTPException(status_code=404, detail="Desk not found")
        db.commit()
        return desk
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{desk_uuid}", response_model=DeskOutSchema)
def delete_desk_endpoint(
    desk_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """刪除桌位（需要桌位管理刪除權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "desk_management", "can_delete"
    )
    try:
        desk = desk_service.delete_desk(db, desk_uuid)
        db.commit()
        return desk
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{desk_uuid}/qrcode", response_model=DeskQRCodeResponse)
def generate_desk_qrcode_api(desk_uuid: str, db: Session = Depends(get_session)):
    """
    生成桌位QR code

    此QR code包含桌位的UUID，顧客可掃描後獲取桌位信息並用於登入
    """
    try:
        # 檢查桌位是否存在
        desk = desk_service.get_desk_by_uuid(db, desk_uuid)
        if not desk:
            raise HTTPException(status_code=404, detail="Desk not found")

        # 生成QR code
        qr_code_base64 = desk_service.generate_desk_qrcode(desk_uuid)

        return {
            "desk_uuid": desk_uuid,
            "desk_name": desk.desk_name,
            "qrcode_base64": qr_code_base64,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
