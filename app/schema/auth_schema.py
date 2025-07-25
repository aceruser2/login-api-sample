from typing import Optional, Union, Dict
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_uuid:str
    user_or_desk: Union[str, int] = None
    extra: Optional[int] = None


class LoginData(BaseModel):
    password: str
    username: Optional[str] = None


class CustomLoginData(BaseModel):
    customer_name: str
    phone: str
    email: str


class CustomDineVerify(BaseModel):
    """顧客內用驗證用 Schema"""

    email: str
    verify_code: str
    desk_uuid: str


class CustomTakeOutVerify(BaseModel):
    """顧客外帶驗證用 Schema"""

    email: str
    verify_code: str
    phone: str
