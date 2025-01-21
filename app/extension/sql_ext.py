from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.pool import NullPool
from typing import Iterator
from app.config import sqlconn

# # pool size 目前暫定50
# db_engine = create_engine(
#     sqlconn.dbconn, query_cache_size=1200, echo=False, poolclass=NullPool, future=True
# )


db_engine = create_engine(
    sqlconn.dbconn,
    pool_size=5,  # 連線池大小
    max_overflow=10,  # 超出連線池大小後可額外分配的連線數
    pool_timeout=30,  # 取得連線時的超時設定
    pool_recycle=1800,  # 連線的回收時間（秒）
    pool_pre_ping=True,
    query_cache_size=1200,
    echo=False,
    future=True
)
# predict 150m/s wait test

session_maker = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine, future=True
    )
scoped_session = ScopedSession(session_maker)

def get_session() -> Iterator[Session]:

    session = scoped_session()
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
    return get_session()


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
