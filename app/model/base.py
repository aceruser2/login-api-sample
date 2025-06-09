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
    func,
)
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import DeclarativeBase
from app.config import sqlconn
from app.extension.sql_ext import scoped_session
from sqlalchemy.orm.scoping import ScopedSession
from typing import Any, Dict


class Base(DeclarativeBase):
    def __repr__(self):
        vals = ",".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if k != "_sa_instance_state"
        )
        return f"<{self.__class__.__name__}({vals})>"


class PGPEncryptString(TypeDecorator):
    impl = String
    cache_ok = True

    class Comparator(TypeDecorator.Comparator):
        def operate(self, op, other, **kwargs):
            return op(pgp_sym_decrypt(self), other, **kwargs)

    @property
    def comparator_factory(self):
        return self.Comparator

    def bind_expression(self, bindvalue):
        bindvalue = type_coerce(bindvalue, String)
        return func.pgp_sym_encrypt(
            bindvalue, sqlconn.pgp_pass, "cipher-algo=aes256, s2k-mode=1"
        )

    def column_expression(self, col):
        return pgp_sym_decrypt(col)


class PGPEncryptJSONB(TypeDecorator):
    impl = JSONB
    cache_ok = True

    def __init__(self, scoped_session: ScopedSession, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scoped_session = scoped_session

    def get_session(self):
        return self.scoped_session()

    def encrypt_value(self, val):
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

    def decrypt_value(self, val):
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

    def process_bind_param(self, value: Dict, dialect: Any):
        if value is None:
            return value
        return self.encrypt_value(value)

    def process_result_value(self, value: Dict, dialect: Any):
        if value is None:
            return value
        return self.decrypt_value(value)


def pgp_sym_decrypt(col: Any):
    return func.pgp_sym_decrypt(func.cast(col, BYTEA), sqlconn.pgp_pass)


encrypted_jsonb_type = PGPEncryptJSONB(scoped_session=scoped_session)
