from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class CreateDeskSchema(BaseModel):
    desk_name: str
    capacity: Optional[int] = 4
    is_available: Optional[bool] = True


class UpdateDeskSchema(BaseModel):
    desk_name: Optional[str] = None
    capacity: Optional[int] = None
    is_available: Optional[bool] = None


class DeskOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    desk_name: str
    capacity: int
    is_available: bool
    soft_delete: bool
    create_dt: datetime
    update_dt: datetime


class DeskBindingRequest(BaseModel):
    customer_email: str
    desk_uuid: str


class DeskBindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    desk_uuid: str
    customer_uuid: UUID
    create_dt: datetime


class ReleaseBindingRequest(BaseModel):
    customer_email: str


class ReleaseBindingResponse(BaseModel):
    message: str


class DeskQRCodeResponse(BaseModel):
    """桌位QR code的回應Schema"""

    desk_uuid: str
    desk_name: str
    qrcode_base64: str  # QR code的base64編碼
