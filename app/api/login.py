from datetime import timedelta
from fastapi import Depends, HTTPException, status
from app import app
from app.config import JwtEnv
from app.adapter.user import get_user_by_username
from app.adapter.custom import (
    get_customer_by_phone,
    create_customer,
    create_desk_customer,
)
from app.adapter.desk import get_desk_by_uuid
from app.extension.sql_ext import get_session, Session
from app.adapter.schema import Token, LoginToken, LoginData, UserData, CustomLoginData
from app.extension.jwt_config import create_access_token, create_refresh_token
from app.adapter.model import User, RoleUser, RolePermission, Permission
from app.extension.jwt_config import refresh_get_current_user


def generate_tokens(user_uuid: str, extra_data: dict = None):
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_uuid, **(extra_data or {})},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user_uuid},
        expires_delta=access_token_expires,
    )
    return access_token, refresh_token


@app.post("/token")
async def login_for_access_token(
    login_data: Union[LoginData, CustomLoginData],  # Updated to accept CustomLoginData
    db: Session = Depends(get_session),
) -> LoginToken:
    user = None
    extra_data = {}
    if isinstance(login_data, LoginData):
        user = get_user_by_username(db, login_data.username)
        if not user or not user.check_password(login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        roles_permissions = (
            db.query(RoleUser, RolePermission, Permission)
            .join(RoleUser, RoleUser.user_uuid == user.uuid)
            .join(RolePermission, RolePermission.role_uuid == RoleUser.role_uuid)
            .join(Permission, Permission.uuid == RolePermission.permission_uuid)
            .all()
        )
        extra_data = {
            "roles": [role.role_uuid for role, _, _ in roles_permissions],
            "permissions": [
                perm.permission_uuid for _, _, perm in roles_permissions
            ],
        }
    elif isinstance(login_data, CustomLoginData):  # Custom login
        user = get_customer_by_phone(db, login_data.phone)
        if not user:
            user = create_customer(db, login_data.custom_name, login_data.phone)
        elif login_data.use_in_restaurants == True:  # Desk customer login
            desk_customer = get_desk_by(db, login_data.desk)
            if not desk_customer:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Desk not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = get_customer_by_phone(db, login_data.username)
            if not user:
                user = create_customer(
                    db, login_data.custom_name, login_data.phone
                )  # 使用者名稱和手機號碼相同
            create_desk_customer(db, login_data.desk, user.uuid)
        elif login_data.userstatus == 2:  # Takeout customer login
            user = get_customer_by_phone(db, login_data.username)
            if not user:
                user = create_customer(
                    db, login_data.username, login_data.username
                )  # 使用者名稱和手機號碼相同
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login data",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = generate_tokens(user.uuid, extra_data)
    return LoginToken(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/refresh")
def refresh(
    db: Session = Depends(get_session),
    refresh_get_current_user: User = Depends(refresh_get_current_user),
) -> Token:
    access_token, _ = generate_tokens(refresh_get_current_user.uuid)
    return Token(access_token=access_token, token_type="bearer")
