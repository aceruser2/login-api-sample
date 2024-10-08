from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app.extension.bcrypt_ext import pwd_context


Base = declarative_base()


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), index=True
    )
    username = Column(String)
    desk_number = Column(Integer)
    user_status = Column(Integer, default=0, comment="0:員工用 1:內用")
    creat_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )

    @hybrid_property
    def password(self):
        """
        getter密碼
        """
        return self._password

    @password.setter  # assign value into bcrypt
    def password(self, value):
        """
        設定密碼class Auth(Base):
        """
        self._password = pwd_context.hash(value)

    @hybrid_method
    def check_password(self, value):
        """
        檢查密碼
        """
        return pwd_context.verify(value, self._password)
