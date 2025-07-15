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
    drivername = os.environ.get("drivername", "postgresql+psycopg2")
    username = os.environ.get(
        "db_user",
    )
    password = os.environ.get(
        "db_pass",
    )
    host = os.environ.get(
        "db_host",
    )
    port = os.environ.get(
        "db_port",
    )
    database = os.environ.get(
        "dbname",
    )
    pgp_pass = os.environ.get("PGP_PASSPHRASE", "gdfgshshtfdjdhdjdgds")


class AdminConfig:
    """Admin user configuration"""

    USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ROLE_NAME = os.environ.get("ADMIN_ROLE", "admin")
    ROLE_LEVEL = int(os.environ.get("ADMIN_ROLE_LEVEL", "9"))
    PERMISSIONS = {
        "user_manage": {
            "can_create": True,
            "can_read": True,
            "can_update": True,
            "can_delete": True,
        },
        "role_manage": {
            "can_create": True,
            "can_read": True,
            "can_update": True,
            "can_delete": True,
        },
    }


class EmailConfig:
    """Email configuration"""

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "your-email@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your-app-password")
    MAIL_FROM = os.environ.get("MAIL_FROM", "your-email@gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
