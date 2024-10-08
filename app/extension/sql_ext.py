from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.pool import NullPool
from typing import Iterator
from app.config import sqlconn

# pool size 目前暫定50
db_engine = create_engine(
    sqlconn.dbconn, query_cache_size=1200, echo=False, poolclass=NullPool, future=True
)


def create_session() -> Iterator[Session]:

    session = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine, future=True
    )
    session = ScopedSession(session)()
    try:
        yield session
    except Exception as ex:
        session.rollback()
        raise ex
    finally:
        session.close()
        db_engine.dispose()


@contextmanager
def use_with_create_session() -> Iterator[Session]:
    return create_session()


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
