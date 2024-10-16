from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from app.config import JwtEnv
from app.extension.bcrypt_ext import pwd_context
from app.adapter.sql_schema import TokenData
from app.adapter.sql_crud import get_user_by_desk, get_user_by_username
from sqlalchemy.orm import Session
from app.extension.sql_ext import create_session
from app.extension.emun_setting import UserStatusEmun

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JwtEnv.SECRET_KEY, algorithm=JwtEnv.ALGORITHM_LOGIN
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=JwtEnv.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, JwtEnv.SECRET_KEY, algorithm=JwtEnv.ALGORITHM_REFRESH
    )
    return encoded_jwt


async def get_current_user(token: str, db: Session = Depends(create_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, JwtEnv.SECRET_KEY, algorithms=[JwtEnv.ALGORITHM_LOGIN]
        )
        user_or_desk: str = payload.get("sub")
        user_status: str = payload.get("extra")
        if user_or_desk is None or user_status is None:
            raise credentials_exception
        token_data = TokenData(user_or_desk=user_or_desk, extra=user_status)
    except InvalidTokenError:
        raise credentials_exception

    user = None
    match token_data.extra:
        case UserStatusEmun.STAFF.value:
            user = get_user_by_username(db=db, user_name=token_data.user_or_desk)
        case UserStatusEmun.DESK.value:
            user = get_user_by_desk(db=db, desk_number=token_data.user_or_desk)
        case _:
            raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


async def refresh_get_current_user(token: str, db: Session = Depends(create_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, JwtEnv.SECRET_KEY, algorithms=[JwtEnv.REFRESH_TOKEN_EXPIRE_DAYS]
        )
        user_or_desk: str = payload.get("sub")
        user_status: str = payload.get("extra")
        if user_or_desk is None or user_status is None:
            raise credentials_exception
        token_data = TokenData(user_or_desk=user_or_desk, extra=user_status)
    except InvalidTokenError:
        raise credentials_exception

    user = None
    match token_data.extra:
        case UserStatusEmun.STAFF.value:
            user = get_user_by_username(db=db, user_name=token_data.user_or_desk)
        case UserStatusEmun.DESK.value:
            user = get_user_by_desk(db=db, desk_number=token_data.user_or_desk)
        case _:
            raise credentials_exception

    if user is None:
        raise credentials_exception
    return user
