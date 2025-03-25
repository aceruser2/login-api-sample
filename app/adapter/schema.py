from typing import List, Optional, Union, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.config import JwtEnv


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_or_desk: Union[str, int] = None
    extra: Optional[int] = None


class UserData(BaseModel):
    uuid: UUID
    username: Optional[str] = None
    desk_number: Optional[int] = None
    info: Optional[Dict]
    email: str
    user_status: int
    creat_dt: datetime
    update_dt: datetime


class LoginData(BaseModel):
    userstatus: int
    password: str
    desk: Optional[str] = None
    username: Optional[str] = None
