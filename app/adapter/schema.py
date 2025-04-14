from typing import List, Optional, Union, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


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
    password: str
    username: Optional[str] = None


class CustomLoginData(BaseModel):
    custom_name: str
    phone: str
    email: str
    use_in_restaurants: bool


class DeskBindingRequest(BaseModel):
    customer_phone: str
    desk_uuid: str


class DeskBindingResponse(BaseModel):
    desk_uuid: str
    customer_uuid: UUID
    create_dt: datetime


class ReleaseBindingRequest(BaseModel):
    customer_phone: str


class ReleaseBindingResponse(BaseModel):
    message: str
