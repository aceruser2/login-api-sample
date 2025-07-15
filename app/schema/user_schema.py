from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """創建用戶的 Schema"""

    username: str
    password: str
    email: Optional[str] = None
    gender: Optional[str] = None
    true_name: Optional[str] = None
    role_uuid: Optional[str] = None


class UserUpdate(BaseModel):
    """更新用戶的 Schema"""

    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    true_name: Optional[str] = None
    role_uuid: Optional[str] = None


class UserData(BaseModel):
    """用戶資料回應的 Schema"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    username: str
    email: Optional[str]
    gender: Optional[str]
    true_name: Optional[str]
    user_status: int
    create_dt: Optional[str]
    update_dt: Optional[str]
