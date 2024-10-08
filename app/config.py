import os
from app.extension.loadenv import load

load()


class Root(object):
    """
    root
    """

    username = os.environ["username"]
    full_name = os.environ["full_name"]
    password = os.environ["password"]
    email = os.environ["email"]
    role = os.environ["role"]
    level = os.environ["level"]
    department_name = os.environ["department_name"]
    description = os.environ["description"]


class MainRole(object):
    """
    role
    """

    ceo = os.environ["ceo"]
    manage = os.environ["manage"]
    maindepart = os.environ["maindepart"]


class JwtEnv(object):
    """
    jwt env
    """

    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM_LOGIN = os.environ["ALGORITHM_LOGIN"]
    ALGORITHM_REFRESH = os.environ["ALGORITHM_REFRESH"]
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ["REFRESH_TOKEN_EXPIRE_DAYS"])


class HostConfig(object):
    host = os.environ["host"]
    port = os.environ["port"]


class sqlconn(object):
    dbconn = os.environ["dbconn"]
