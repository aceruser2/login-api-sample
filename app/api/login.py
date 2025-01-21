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
from app.adapter.sql_schema import Token, LoginToken
from app.extension.jwt_config import (
    create_access_token,
    get_current_user,
    create_refresh_token,
    refresh_get_current_user,
)
from app.extension.emun_setting import UserStatusEmun
from app.adapter.sql_schema import UserData
from app.adapter.sql_adapter import User

@app.post("/token")
async def login_for_access_token(
    userstatus: int,
    password: str,
    desk: str = None,
    username: str = None,
    db: Session = Depends(get_session),
) -> LoginToken:
    user = None

    match userstatus:
        case UserStatusEmun.STAFF.value:
            user = sql_crud.get_user_by_username(db, username)
        case UserStatusEmun.DESK.value:
            user = sql_crud.get_user_by_desk(db, desk)
        case _:
            raise HTTPException(status_code=400, detail="login error")

    if not user: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.check_password(value=password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = None
    match userstatus:
        case UserStatusEmun.STAFF.value:
            access_token = create_access_token(
                data={"sub": user.username, "extra": userstatus},
                expires_delta=access_token_expires,
            )
            refresh_token = create_refresh_token(
                data={"sub": user.username, "extra": userstatus},
                expires_delta=access_token_expires,
            )
        case UserStatusEmun.DESK.value:
            access_token = create_access_token(
                data={"sub": user.desk_number, "extra": userstatus},
                expires_delta=access_token_expires,
            )
            refresh_token = create_refresh_token(
                data={"sub": user.desk_number, "extra": userstatus},
                expires_delta=access_token_expires,
            )
    if access_token is None:
        raise HTTPException(status_code=400, detail="login error")
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
