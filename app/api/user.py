import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from fastapi import Depends
from app.extension.sql_ext import create_session
from fastapi.responses import JSONResponse
from app import app
from app.adapter import sql_crud, sql_schema
from app.handler.vaild import errmsn
from sqlalchemy.orm import Session
from app.extension.jwt_config import get_current_user

log = logging.getLogger(__name__)


@app.post("/creat_user/", response_model=sql_schema.UserData)
def creat_user(
    db: Session = Depends(create_session),
    current_user: sql_schema.UserData = Depends(get_current_user),
    user_status: int = 0,
    username: str = None,
    desk_number: str = None,
    password: str = None,
):

    try:
        user = sql_crud.create_user(
            user_status=user_status,
            username=username,
            desk_number=desk_number,
            password=password,
            db=db,
        )
        return user

    except Exception as e:
        log.critical(e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )


# @app.get("/get_users/", response_model=List[sql_schema.UserAuthInfo])
# def get_users(
#     last_uuid: Optional[UUID] = None,
#     skip: int = 0,
#     limit: int = 100,
#     Authorize: AuthJWT = Depends(),
# ):
#     Authorize.jwt_required()
#     users = None
#     if not last_uuid:
#         users = sql_crud.get_users(skip, limit)
#     else:
#         users = sql_crud.get_users_flag(last_uuid, skip, limit)
#     if not users:
#         return JSONResponse(status_code=400, content={"message": "users is not exist"})
#     return users
