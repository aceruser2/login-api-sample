import qrcode
import base64
from io import BytesIO
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schema.qrcode_schema import QRCodeResponse
from datetime import datetime

log = logging.getLogger(__name__)


def generate_desk_qrcode(desk_uuid: str, size: int = 200) -> str:
    """
    生成包含桌位UUID的QR code，並返回base64編碼的圖像

    Args:
        desk_uuid: 桌位的唯一識別碼
        size: QR code的尺寸（像素）

    Returns:
        str: QR code的base64編碼字符串
    """
    try:
        # 創建QR code數據
        data = {"type": "desk", "desk_uuid": desk_uuid}

        # 使用JSON將數據轉換為字符串
        import json

        data_str = json.dumps(data)

        # 創建QR code圖像
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_str)
        qr.make(fit=True)

        # 創建圖像
        img = qr.make_image(fill_color="black", back_color="white")

        # 將圖像轉換為base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str
    except Exception as e:
        log.error(f"Failed to generate QR code: {str(e)}")
        raise ValueError("QR code generation failed")


def process_qrcode(qr_data: str, db: Session) -> QRCodeResponse:
    """
    Process the scanned QR code data
    """
    # Parse the QR code data - implement your business logic here
    # For example, it might be a JSON string or a specific format

    # Example implementation - replace with your actual logic
    try:
        # Here you would decode and validate the QR code data
        # For example, check if it's a valid order, coupon, etc.

        # Return appropriate response
        return QRCodeResponse(
            success=True,
            message="QR code processed successfully",
            data={
                "scanned_at": datetime.now().isoformat(),
                "qr_type": "sample_type",  # Replace with actual type detection
                "content": qr_data,
            },
        )
    except Exception as e:
        raise ValueError(f"Invalid QR code: {str(e)}")
