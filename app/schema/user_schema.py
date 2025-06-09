from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserData(BaseModel):
    uuid: UUID
    username: Optional[str] = None
    desk_number: Optional[int] = None
    info: Optional[Dict]
    email: str
    user_status: int
    creat_dt: datetime
    update_dt: datetime
