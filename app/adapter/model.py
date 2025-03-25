import bcrypt
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    BINARY,
    text,
    TypeDecorator,
    type_coerce,
    ColumnElement,
    Dialect,
    FunctionElement,
    Enum as SQLAlchemyEnum,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.dialects.postgresql import BYTEA, JSON, JSONB
from sqlalchemy.sql.operators import OperatorType
from sqlalchemy import event
from typing import Any, ClassVar, Dict
from app.config import sqlconn
from sqlalchemy.orm import DeclarativeBase
from app.extension.sql_ext import use_with_create_session
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.scoping import ScopedSession
from app.extension.sql_ext import scoped_session
from app.extension.emun_setting import UserStatusEnum


class Base(DeclarativeBase):
    def __repr__(self: "Base") -> str:
        """Return a string representation of the object."""
        vals: str = ",".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if k != "_sa_instance_state"
        )

        return f"<{self.__class__.__name__}({vals})>"


class PGPEncryptString(TypeDecorator):
    # https://gist.github.com/sluipmoord/05bde6f54875283b4dfce040120ee2d6
    """A type for storing encrypted strings in the database.
    This type encrypts the data server side using the pgcrypto extension's pgp_sym_encrypt function when storing it in
    the database. The data is decrypted using the pgp_sym_decrypt function when it is read from the database.
    Typical usage::
        class MyModel(Base):
            __tablename__ = "my_model"
            id = Column(Integer, primary_key=True)
            encrypted_string: Mapped[str] = mapped_column(PGPEncryptString())
        # Inserting data
        encrypted_string = "my secret data"
        my_model = MyModel(encrypted_string=encrypted_string)
        db.session.add(my_model)
        db.session.commit()
        # Filtering data
        my_model = db.session.query(MyModel).filter(
            MyModel.encrypted_string == "my secret data"
        ).first()
    """

    impl = String
    cache_ok = True

    class Comparator(TypeDecorator.Comparator):
        """Custom comparator for PGPEncryptString."""

        def operate(
            self: "PGPEncryptString.Comparator",
            op: OperatorType,
            other: Any,
            **kwargs: Any,
        ) -> ColumnElement[Any]:
            return op(pgp_sym_decrypt(self), other, **kwargs)

    @property
    def comparator_factory(self: "PGPEncryptString") -> Any:
        return self.Comparator

    def bind_expression(self: "PGPEncryptString", bindvalue: Any):

        bindvalue = type_coerce(bindvalue, String)
        return func.pgp_sym_encrypt(
            bindvalue, sqlconn.pgp_pass, "cipher-algo=aes256, s2k-mode=1"
        )

    def column_expression(self: "PGPEncryptString", col: Any):
        return pgp_sym_decrypt(col)


class PGPEncryptJSONB(TypeDecorator):
    impl = JSONB
    cache_ok = True

    def __init__(self, scoped_session: ScopedSession, *args, **kwargs):
        """
        Initialize the type decorator with a scoped session.
        """
        super().__init__(*args, **kwargs)
        self.scoped_session = scoped_session

    def get_session(self) -> Session:
        """
        Retrieve the current thread-local session from ScopedSession.
        """
        return self.scoped_session()

    def encrypt_value(self, val: Any) -> Any:
        """
        Encrypt a value using pgcrypto functions.
        """
        session = self.get_session()
        if isinstance(val, dict):
            return {k: self.encrypt_value(v) for k, v in val.items()}
        if isinstance(val, list):
            return [self.encrypt_value(v) for v in val]

        return session.query(
            func.cast(
                func.pgp_sym_encrypt(
                    func.cast(val, String),
                    sqlconn.pgp_pass,
                    "cipher-algo=aes256, s2k-mode=1",
                ),
                String,
            )
        ).scalar()

    def decrypt_value(self, val: Any) -> Any:
        """
        Decrypt a value using pgcrypto functions.
        """
        session = self.get_session()
        if isinstance(val, dict):
            return {k: self.decrypt_value(v) for k, v in val.items()}
        if isinstance(val, list):
            return [self.decrypt_value(v) for v in val]

        return session.query(
            func.pgp_sym_decrypt(
                val,
                sqlconn.pgp_pass,
                "cipher-algo=aes256, s2k-mode=1",
            )
        ).scalar()

    def process_bind_param(self, value: Dict, dialect: Any) -> Any:
        """
        Process values before binding them to the database.
        """
        if value is None:
            return value
        return self.encrypt_value(value)

    def process_result_value(self, value: Dict, dialect: Any) -> Any:
        """
        Process values after retrieving them from the database.
        """
        if value is None:
            return value
        return self.decrypt_value(value)


encrypted_jsonb_type = PGPEncryptJSONB(scoped_session=scoped_session)


def pgp_sym_decrypt(col: Any) -> FunctionElement:

    return func.pgp_sym_decrypt(func.cast(col, BYTEA), sqlconn.pgp_pass)


class User(Base):
    """使用者(店員老闆3-5人)

    Args:
        Base (_type_): _description_

    Returns:
        _type_: _description_
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    username = Column(String)
    _password = Column(BYTEA)
    email = Column(PGPEncryptString(), unique=True, nullable=False)
    info = Column(encrypted_jsonb_type)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
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
        self._password = bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt())

    @hybrid_method
    def check_password(self, value):
        """
        檢查密碼
        """
        if not self._password:  # 防止 None 值
            return False

        return bcrypt.checkpw(value.encode("utf-8"), self._password)


class Role(Base):
    """餐廳角色跟權限"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    role_name = Column(String)
    level = Column(Integer)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class RoleUser(Base):
    __tablename__ = "role_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(String)
    role_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class Permission(Base):
    """permission_attributes {"can_edit": true, "can_delete": true, "fields": ["name", "email", "phone"]}
        edit_user
    Args:
        Base (_type_): _description_
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    permission_name = Column(String)
    permission_attributes = Column(JSONB)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_uuid = Column(String)
    permission_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    customer_name = Column(String)
    customer_phone = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class Desk(Base):
    __tablename__ = "desks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    desk_name = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )


class DeskCustomer(Base):
    # 訂單成立才key可能不同天同桌同人
    __tablename__ = "desk_customer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    desk_uuid = Column(String)
    customer_uuid = Column(String)
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now()),
    )
