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
)
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.dialects.postgresql import BYTEA, JSON, JSONB
from sqlalchemy.sql.operators import OperatorType
from sqlalchemy import event
from typing import Any, ClassVar
from app.config import sqlconn
from sqlalchemy.orm import DeclarativeBase
from app.extension.sql_ext import use_with_create_session
 

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
    """A type for storing encrypted JSONB data in the database.
    This type encrypts the data server side using the pgcrypto extension's pgp_sym_encrypt function before storing it in
    the database. It loops through the JSONB data and encrypts each value individually. This allows for searching and
    filtering on the encrypted data.
    The data is decrypted using the pgp_sym_decrypt function when it is read from the database. The type attempts to
    infer the primitive type of the decrypted data and return it as a Python primitive type.
    Typical usage::
        class MyModel(Base):
            __tablename__ = "my_model"
            id = Column(Integer, primary_key=True)
            encrypted_data: Mapped[str] = mapped_column(PGPEncryptJSONB())
        # Inserting data
        data = {"key": "value", "count": 1}
        my_model = MyModel(encrypted_data=data)
        db.session.add(my_model)
        db.session.commit()
        # Filtering data
        my_model = db.session.query(MyModel).filter(
            MyModel.encrypted_data["key"].astext == "value"
        ).first()
        my_model = db.session.query(MyModel).filter(
            MyModel.encrypted_data["count"].astext.cast(Integer) == 1
        ).first()
    """

    impl = JSONB
    cache_ok = True

    class Comparator(JSON.Comparator):
        """Custom comparator for PGPEncryptJSONB."""

        # add custom operators here
        @property
        def astext(self: "PGPEncryptJSONB.Comparator") -> Any:
            res = super().astext

            return pgp_sym_decrypt(res)

    @property
    def comparator_factory(self: "PGPEncryptJSONB") -> Any:
        return self.Comparator

    def infer_primitive_type(
        self: "PGPEncryptJSONB", value: str
    ) -> bool | int | float | str:
        if value.lower() in ["true", "false"]:
            return bool(value)

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value

    def process_bind_param(
        self: "PGPEncryptJSONB", value: dict, dialect: Dialect
    ) -> dict[Any, Any] | list[Any] | Any:  # noqa: ARG002

        if value is None:
            return value

        def encrypt_value(val: Any) -> dict[Any, Any] | list[Any] | Any:
            if isinstance(val, dict):
                return {k: encrypt_value(v) for k, v in val.items()}

            if isinstance(val, list):
                return [encrypt_value(v) for v in val]
            # wait vaild
            with use_with_create_session() as db:
                return db.session.query(
                    func.cast(
                        func.pgp_sym_encrypt(
                            func.cast(val, String),
                            sqlconn.pgp_pass,
                            "cipher-algo=aes256, s2k-mode=1",
                        ),
                        String,
                    )
                ).scalar()

        return encrypt_value(value)

    def process_result_value(
        self: "PGPEncryptJSONB",
        value: dict,
        dialect: Dialect,  # noqa: ARG002
    ) -> dict[Any, Any] | list[Any] | Any:

        if value is None:
            return value

        def decrypt_value(val: Any) -> dict[Any, Any] | list[Any] | Any:
            if isinstance(val, dict):
                return {k: decrypt_value(v) for k, v in val.items()}
            if isinstance(val, list):
                return [decrypt_value(v) for v in val]
            with use_with_create_session() as db:
                result = db.session.query(
                    func.pgp_sym_decrypt(
                        val,
                        sqlconn.pgp_pass,
                        "cipher-algo=aes256, s2k-mode=1",
                    )
                ).scalar()
                return self.infer_primitive_type(result)

        return decrypt_value(value)


def pgp_sym_decrypt(col: Any) -> FunctionElement:

    return func.pgp_sym_decrypt(func.cast(col, BYTEA), sqlconn.pgp_pass)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        String, server_default=text("uuid_generate_v4()"), index=True
    )
    username = Column(String)
    _password = Column(BYTEA)
    email = Column(String)
    info = Column(JSONB)
    desk_number = Column(Integer)
    user_status = Column(Integer, default=0, comment="0:員工用 1:內用")
    active = Column(Boolean, default=False, comment="0:沒登入用 1:登入用")
    soft_delete = Column(Boolean, default=False)
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
        self._password = bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt())

    @hybrid_method
    def check_password(self, value):
        """
        檢查密碼
        """
        return bcrypt.checkpw(value.encode("utf-8"), self._password)






