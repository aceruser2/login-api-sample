from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


class LoginData(BaseModel):
    username: str
    password: str


class TokenData(BaseModel):
    user_uuid: Optional[str] = None


class RoleInfo(BaseModel):
    role_uuid: str
    role_name: str
    level: int


class PermissionInfo(BaseModel):
    permission_uuid: str
    permission_name: str
    attributes: Dict[str, bool]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    # 新增角色和權限資訊
    roles: List[RoleInfo] = []
    permissions: List[PermissionInfo] = []


class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class CustomLoginData(BaseModel):
    customer_name: str
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
