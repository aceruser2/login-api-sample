from sqlalchemy import Column, String, Boolean, Integer, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app.model.base import Base, PGPEncryptString, encrypted_jsonb_type
import bcrypt
import logging

log = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    username = Column(String)
    _password = Column(String)
    email = Column(PGPEncryptString(), unique=True, nullable=False)
    info = Column(encrypted_jsonb_type)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """設置密碼時自動加密"""
        if value:
            # 統一使用 utf-8 編碼
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(value.encode("utf-8"), salt)
            # 將 bytes 轉為 string 存儲，保持一致性
            self._password = hashed.decode("utf-8")
        else:
            self._password = None

    @hybrid_method
    def check_password(self, value: str) -> bool:
        """檢查密碼"""
        if not self._password or not value:
            return False

        try:
            # 確保存儲的密碼是 bytes 格式進行比較
            if isinstance(self._password, str):
                stored_password = self._password.encode("utf-8")
            else:
                stored_password = self._password

            # 確保輸入密碼是 str 格式
            if isinstance(value, bytes):
                check_value = value.decode("utf-8")
            else:
                check_value = value

            result = bcrypt.checkpw(check_value.encode("utf-8"), stored_password)
            log.debug(f"Password check for user {self.username}: {result}")
            return result

        except Exception as e:
            log.error(f"Password check failed for user {self.username}: {e}")
            return False


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    role_name = Column(String)
    level = Column(Integer)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class RoleUser(Base):
    __tablename__ = "role_user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(String)
    role_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    permission_name = Column(String)
    permission_attributes = Column(JSONB)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )


class RolePermission(Base):
    __tablename__ = "role_permission"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_uuid = Column(String)
    permission_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=text("timezone('utc', now())"))
    update_dt = Column(
        DateTime,
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
