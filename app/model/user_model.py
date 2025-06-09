from sqlalchemy import Column, String, Boolean, Integer, DateTime, text, JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app.model.base import Base, PGPEncryptString, encrypted_jsonb_type
import bcrypt


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
        self._password = bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt())

    @hybrid_method
    def check_password(self, value):
        if not self._password:
            return False
        return bcrypt.checkpw(value.encode("utf-8"), self._password)


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
