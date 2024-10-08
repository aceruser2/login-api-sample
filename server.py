import os
import uvicorn
import logging.config
from app import logging_config
from app.adapter.sql_adapter import User, Role, Department, Auth
from app import app
from app.extension.sql_ext import Db
from app.adapter.sql_schema import Settings
from app.config import HostConfig
from app.config import Root
from app.adapter.sql_crud import get_user, create_root


def steup():

    logging.config.dictConfig(logging_config.DEV)


steup()

if __name__ == "__main__":

    uvicorn.run(app, host=HostConfig.host, port=int(HostConfig.port))
