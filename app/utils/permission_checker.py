from typing import Tuple, Dict, Any
from fastapi import HTTPException, status
from app.services.user_service import get_user_all_role_and_permission_by_user_uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql.expression import false
import logging

log = logging.getLogger(__name__)


class PermissionChecker:
    """權限檢查工具類"""

    @staticmethod
    def require_admin(user_data: Tuple, db: Session):
        """檢查是否為管理員"""
        user_object, user_type = user_data
        if user_type != "staff":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required."
            )

        # 檢查用戶是否有管理員權限
        permissions = get_user_all_role_and_permission_by_user_uuid(
            db, user_object.uuid
        )

        for user, role, permission in permissions:
            if role and role.role_name.lower() == "admin" and role.level >= 9:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin level access required."
        )

    @staticmethod
    def require_staff_with_permission(
        user_data: Tuple, db: Session, required_permission: str, required_action: str
    ):
        """檢查員工是否有特定權限"""
        user_object, user_type = user_data
        if user_type != "staff":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required."
            )

        # 獲取用戶所有權限
        permissions = get_user_all_role_and_permission_by_user_uuid(
            db, user_object.uuid
        )

        for user, role, permission in permissions:
            if permission and permission.permission_name == required_permission:
                attributes = permission.permission_attributes or {}
                if attributes.get(required_action, False):
                    return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission}.{required_action} required.",
        )

    @staticmethod
    def require_staff_basic(user_data: Tuple):
        """基本員工權限檢查"""
        user_object, user_type = user_data
        if user_type != "staff":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required."
            )

    @staticmethod
    def check_user_permissions(user_data: Tuple, db: Session) -> Dict[str, Any]:
        """獲取用戶所有權限"""
        user_object, user_type = user_data
        if user_type != "staff":
            return {"permissions": [], "is_admin": False}

        permissions = get_user_all_role_and_permission_by_user_uuid(
            db, user_object.uuid
        )
        user_permissions = []
        is_admin = False

        for user, role, permission in permissions:
            if role and role.role_name.lower() == "admin" and role.level >= 9:
                is_admin = True

            if permission:
                user_permissions.append(
                    {
                        "permission_name": permission.permission_name,
                        "attributes": permission.permission_attributes,
                    }
                )

        return {"permissions": user_permissions, "is_admin": is_admin}
