import os
import uvicorn
import logging.config
from app import logging_config
from app.adapter.model import User, Role, Permission, RoleUser, RolePermission
from app.adapter.user import get_user_by_username, create_role, create_permission
from app import app
from app.config import HostConfig, AdminConfig
from app.extension.sql_ext import db_engine, use_with_create_session
from fastapi.middleware.cors import CORSMiddleware


def create_admin():
    with use_with_create_session() as db:
        # Create admin role first
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

        # Create admin user if not exists
        admin = get_user_by_username(db=db, username=AdminConfig.USERNAME)
        if not admin:
            admin = User(
                username=AdminConfig.USERNAME,
                email=AdminConfig.EMAIL,
                info={"gender": "male", "true_name": "Administrator"},
                password=AdminConfig.PASSWORD,
            )
            db.add(admin)
            db.flush()

            # Link admin user to admin role
            role_user = RoleUser(user_uuid=admin.uuid, role_uuid=admin_role.uuid)
            db.add(role_user)

        db.commit()


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
