import os
import uvicorn
import logging.config
from app import logging_config
from app.adapter.model import User, Role, Permission, RoleUser, RolePermission
from app.adapter.user import (
    get_user_by_username,
    create_role,
    create_permission,
    create_user,
)
from app import app
from app.config import HostConfig, AdminConfig
from app.extension.sql_ext import db_engine, use_with_create_session
from fastapi.middleware.cors import CORSMiddleware


def create_admin():
    with use_with_create_session() as db:

        # Create admin user if not exists
        admin = get_user_by_username(db=db, username=AdminConfig.USERNAME)
        if not admin:
            admin_role = create_role(
                db=db, role_name=AdminConfig.ROLE_NAME, level=AdminConfig.ROLE_LEVEL
            )

            # Create admin permissions
            permissions = []
            for perm_name, perm_attrs in AdminConfig.PERMISSIONS.items():
                perm = create_permission(
                    db=db, permission_name=perm_name, permission_attributes=perm_attrs
                )
                permissions.append(perm)

                # Link permission to admin role
                role_perm = RolePermission(
                    role_uuid=admin_role.uuid, permission_uuid=perm.uuid
                )
                db.add(role_perm)

            # 請確認 sqlconn.pgp_pass 與資料庫一致，否則加密/解密會失敗
            create_user(
                db=db,
                username=AdminConfig.USERNAME,
                password=AdminConfig.PASSWORD,
                email=AdminConfig.EMAIL,
                gender="male",
                true_name="Administrator",
                role_uuid=admin_role.uuid,
            )
            db.commit()

        # 若解密異常，請檢查：
        # 1. sqlconn.pgp_pass 是否與資料庫現有加密資料一致
        # 2. 若金鑰有變動，需清空資料表或重建資料庫
        # 3. 請勿用不同金鑰混用同一批資料


def steup():
    create_admin()
    logging.config.dictConfig(logging_config.DEV)


steup()

if __name__ == "__main__":
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(app, host=HostConfig.host, port=int(HostConfig.port))
