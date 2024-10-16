import os
import uvicorn
import logging.config
from app import logging_config
from app.adapter.sql_adapter import User
from app import app
from app.config import HostConfig


def steup():

    logging.config.dictConfig(logging_config.DEV)


steup()

if __name__ == "__main__":

    uvicorn.run(app, host=HostConfig.host, port=int(HostConfig.port))
