from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from starlette.responses import JSONResponse
from app import app
from app.handler.for_map import auth
from app.config import JwtEnv
from app.adapter import sql_crud
from typing import Annotated
from app.extension.sql_ext import get_session, Session
from app.adapter.body_schema import Token, LoginToken,LoginData
from app.extension.jwt_config import (
    create_access_token,
    get_current_user,
    create_refresh_token,
    refresh_get_current_user,
)
from app.adapter.body_schema import UserData
from app.adapter.sql_adapter import User

#TODO: rabc待調整
@app.post("/token")
async def login_for_access_token(
    login_data: LoginData,
    db: Session = Depends(get_session),
) -> LoginToken:
    """
    STAFF = 0      # 員工
    DESK = 1       # 內用顧客
    CUSTOMER = 2   # 外帶顧客
    DELIVERY = 3   # 外送員
    ADMIN = 4      # 管理員
    可以被這些角色登入
    但期望內用角色

    Args:
        login_data (LoginData): _description_
        db (Session, optional): _description_. Defaults to Depends(get_session).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        LoginToken: _description_
    """

    user: User = sql_crud.get_user_by_login_info(db, login_data)
   
    if not user: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.check_password(value=login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.uuid},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.uuid},
        expires_delta=access_token_expires,
    )

    return LoginToken(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/refresh")
def refresh(
    db: Session = Depends(get_session),
    refresh_get_current_user: User = Depends(refresh_get_current_user),
) -> Token:

    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    match refresh_get_current_user.user_status:

        case UserStatusEmun.STAFF.value:
            access_token = create_access_token(
                data={
                    "sub": refresh_get_current_user.username,
                    "extra": refresh_get_current_user.user_status,
                },
                expires_delta=access_token_expires,
            )
        case UserStatusEmun.DESK.value:
            access_token = create_access_token(
                data={
                    "sub": refresh_get_current_user.username,
                    "extra": refresh_get_current_user.user_status,
                },
                expires_delta=access_token_expires,
            )
        case _:
            raise HTTPException(status_code=400, detail="login error")

    return Token(access_token=access_token, token_type="bearer")
