from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
import bcrypt
from app.config import JwtEnv
from app.schema import TokenData
from app.services.user_service import get_user_by_username
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


async def get_current_user(
    bearer: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"token": "Bearer"},
    )

    try:
        token = None
        if bearer:
            token = str(bearer.credentials)
        if not token:
            raise credentials_exception
        payload = jwt.decode(
            token, JwtEnv.SECRET_KEY, algorithms=[JwtEnv.ALGORITHM_LOGIN]
        )
        user: str = payload.get("sub")
        if user is None:
            raise credentials_exception
        return user

    except InvalidTokenError:
        raise credentials_exception


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
