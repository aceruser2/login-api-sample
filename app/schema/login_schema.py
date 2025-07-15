from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginData(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class CustomLoginData(BaseModel):
    custom_name: str
    phone: str
    email: EmailStr


class CustomTakeOutVerify(BaseModel):
    email: EmailStr
    verify_code: str


class CustomDineVerify(BaseModel):
    email: EmailStr
    verify_code: str
    desk_uuid: str


class DeskBindingRequest(BaseModel):
    customer_email: EmailStr
    desk_uuid: str


class DeskBindingResponse(BaseModel):
    desk_uuid: str
    customer_uuid: str
    create_dt: datetime


class ReleaseBindingRequest(BaseModel):
    customer_email: EmailStr


class ReleaseBindingResponse(BaseModel):
    message: str
