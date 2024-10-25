import os
from app.extension.loadenv import load

load()


class JwtEnv(object):
    """
    jwt env
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "norgjosrejgorejgojerogj")
    ALGORITHM_LOGIN = os.environ.get("ALGORITHM_LOGIN", "HS256")
    ALGORITHM_REFRESH = os.environ.get("ALGORITHM_REFRESH", "HS384")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 999999)
    )
    REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 9999999)
    )


class HostConfig(object):
    host = os.environ.get("host", "0.0.0.0")
    port = os.environ.get("port", 8000)


class sqlconn(object):
    dbconn = os.environ.get(
        "dbconn", "postgresql+psycopg2://user:password@localhost/dbname"
    )
    pgp_pass = os.environ.get("PGP_PASSPHRASE", "gdfgshshtfdjdhdjdgds")
