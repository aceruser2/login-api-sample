from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from pydantic import EmailStr
from app.config import EmailConfig

conf = ConnectionConfig(
    MAIL_USERNAME=EmailConfig.MAIL_USERNAME,
    MAIL_PASSWORD=EmailConfig.MAIL_PASSWORD,
    MAIL_FROM=EmailConfig.MAIL_FROM,
    MAIL_PORT=EmailConfig.MAIL_PORT,
    MAIL_SERVER=EmailConfig.MAIL_SERVER,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)


async def send_verification_email(email: str, code: str):
    """Send verification code via email"""
    message = MessageSchema(
        subject="Restaurant Login Verification Code",
        recipients=[email],
        body=f"""
        Your verification code is: {code}
        
        This code will expire in 15 minutes.
        You can request a new code after 5 minutes.
        """,
        subtype="plain",
    )

    fastmail = FastMail(conf)
    await fastmail.send_message(message)
