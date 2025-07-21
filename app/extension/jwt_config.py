from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, PyJWTError
from pydantic import BaseModel
from typing import Optional, List, Tuple, Union
import bcrypt
from app.config import JwtEnv
from app.schema import TokenData
from app.services.user_service import get_user_by_uuid
from app.services.custom_service import get_customer_by_uuid
from app.model import User, Customer
from sqlalchemy.orm import Session
from app.extension.sql_ext import get_session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()

auth_scheme = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


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


async def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
) -> Tuple[Union[User, Customer], str]:
    """獲取當前用戶，返回 (用戶物件, 用戶類型) 的元組"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, JwtEnv.SECRET_KEY, algorithms=[JwtEnv.ALGORITHM_LOGIN]
        )
        user_uuid: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if user_uuid is None:
            raise credentials_exception

        token_data = TokenData(user_uuid=user_uuid)
    except PyJWTError:
        raise credentials_exception
    if user_type == "staff":
        user = get_user_by_uuid(db, user_uuid=token_data.user_uuid)
        if user is None:
            raise credentials_exception
        return user, user_type
    if user_type == "customer":
        customer = get_customer_by_uuid(db, customer_uuid=token_data.user_uuid)
        if customer is None:
            raise credentials_exception

        return customer, user_type


async def get_current_active_user(
    current_user: Tuple[Union[User, Customer], str] = Depends(get_current_user),
):
    """獲取當前活躍用戶"""
    user_object, user_type = current_user
    if user_object.soft_delete:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def refresh_get_current_user(
    bearer: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        refresh_token = None
        if bearer:
            refresh_token = str(bearer.credentials)
        if not refresh_token:
            raise credentials_exception
        payload = jwt.decode(
            refresh_token,
            JwtEnv.SECRET_KEY,
            algorithms=[JwtEnv.ALGORITHM_REFRESH],
        )
        user: str = payload.get("sub")
        if user is None:
            raise credentials_exception
        return user

    except InvalidTokenError:
        raise credentials_exception
