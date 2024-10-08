from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.config import JwtEnv


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserData(BaseModel):
    uuid: UUID
    username: str
    desk_number: int
    user_status: str
    creat_dt: datetime
    update_dt: datetime
