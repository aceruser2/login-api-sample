import os
import uvicorn
import logging.config
from app import logging_config
from app.adapter.sql_adapter import User
from app.adapter.sql_crud import get_user_by_username
from app import app
from app.config import HostConfig
from app.adapter.sql_adapter import Base
from app.extension.sql_ext import db_engine, use_with_create_session


def create_admin():
    with use_with_create_session() as db:

        user = get_user_by_username(db=db, user_name="admin")
        if not user:
            user = User(
                username="admin",
                email="admin@gmail.com",
                info={"gender": "male", "true_name": "adm"},
                password="123456",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            vaild = get_user_by_username(db=db, user_name="admin")
            print(vaild.email == "admin@gmail.com")
            print(vaild.info["gender"] == "male")


def steup():
    create_admin()
    logging.config.dictConfig(logging_config.DEV)


steup()

if __name__ == "__main__":

    uvicorn.run(app, host=HostConfig.host, port=int(HostConfig.port))
