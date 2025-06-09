from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class DeskBindingRequest(BaseModel):
    customer_email: str
    desk_uuid: str


class DeskBindingResponse(BaseModel):
    desk_uuid: str
    customer_uuid: UUID
    create_dt: datetime


class ReleaseBindingRequest(BaseModel):
    customer_email: str


class ReleaseBindingResponse(BaseModel):
    message: str
