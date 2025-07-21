from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from app import app
from app.services.user_service import (
    get_user_all_role_and_permission,
    create_user,
    delete_user,
    get_user_by_uuid,
    assign_permission_to_user,
    remove_permission_from_user,
    get_all_roles,
    get_all_permissions,
)
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.schema import UserData
from app.utils.permission_checker import PermissionChecker
import logging

log = logging.getLogger(__name__)


def require_admin(user_data: Tuple, db: Session):
    """檢查管理員權限"""
    return PermissionChecker.require_admin(user_data, db)


def require_user_management_permission(user_data: Tuple, db: Session):
    """檢查用戶管理權限"""
    return PermissionChecker.require_staff_with_permission(
        user_data, db, "user_management", "can_read"
    )


@app.get("/users/me")
async def get_current_user_info(
    user_data: Tuple = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """獲取當前用戶信息"""
    user_object, user_type = user_data
    try:
        if user_type == "staff":
            user = get_user_by_uuid(db, user_object.uuid)
        else:
            user = user_object
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_uuid}")
async def get_user_info(
    user_uuid: str,
    user_data: Tuple = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """獲取指定用戶信息（需要用戶管理權限）"""
    require_user_management_permission(user_data, db)
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
    user_data: Tuple = Depends(get_current_user),
):
    """刪除使用者（需要用戶管理刪除權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "user_management", "can_delete"
    )
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
    user_data: Tuple = Depends(get_current_user),
):
    """創建新使用者（需要用戶管理創建權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "user_management", "can_create"
    )
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


@app.post("/users/{user_uuid}/assign-role")
async def assign_role_to_user(
    user_uuid: str,
    role_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """為用戶分配角色（僅限管理員）"""
    require_admin(user_data, db)
    try:
        result = assign_permission_to_user(
            db=db, user_uuid=user_uuid, role_uuid=role_uuid
        )
        db.commit()
        return {"message": "Role assigned successfully", "role_user_id": result.id}
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_uuid}/remove-role")
async def remove_role_from_user(
    user_uuid: str,
    role_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """移除用戶角色（僅限管理員）"""
    require_admin(user_data, db)
    try:
        remove_permission_from_user(db=db, user_uuid=user_uuid, role_uuid=role_uuid)
        db.commit()
        return {"message": "Role removed successfully"}
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/roles/")
async def list_all_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取所有角色（需要權限管理權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "role_management", "can_read"
    )
    try:
        return get_all_roles(db=db, skip=skip, limit=limit)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/permissions/")
async def list_all_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取所有權限（需要權限管理權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "role_management", "can_read"
    )
    try:
        return get_all_permissions(db=db, skip=skip, limit=limit)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_uuid}/permissions")
async def get_user_permissions(
    user_uuid: str,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取用戶權限詳情（僅限管理員）"""
    require_admin(user_data, db)
    try:
        # 模擬獲取特定用戶的權限
        user_data_temp = (get_user_by_uuid(db, user_uuid), "staff")
        permissions = PermissionChecker.check_user_permissions(user_data_temp, db)
        return permissions
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/me/permissions")
async def get_current_user_permissions(
    user_data: Tuple = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """獲取當前用戶的角色權限信息"""
    user_object, user_type = user_data

    if user_type != "staff":
        return {"roles": [], "permissions": []}  # 顧客沒有角色權限

    try:
        # 獲取用戶的角色和權限信息
        roles_permissions = get_user_all_role_and_permission(db, user_object)

        # 提取角色和權限信息
        roles_data = []
        permissions_data = []

        for user_obj, role_obj, permission_obj in roles_permissions:
            if role_obj and role_obj.uuid not in [r.get("uuid") for r in roles_data]:
                roles_data.append(
                    {
                        "uuid": role_obj.uuid,
                        "role_name": role_obj.role_name,
                        "level": role_obj.level,
                    }
                )

            if permission_obj and permission_obj.uuid not in [
                p.get("uuid") for p in permissions_data
            ]:
                permissions_data.append(
                    {
                        "uuid": permission_obj.uuid,
                        "permission_name": permission_obj.permission_name,
                        "attributes": permission_obj.permission_attributes,
                    }
                )

        return {"roles": roles_data, "permissions": permissions_data}
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
