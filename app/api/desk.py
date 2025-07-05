from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import app
from app.services.desk_service import (
    create_desk,
    get_desk_by_uuid,
    get_all_desks,
    update_desk,
    delete_desk,
)
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
import logging

log = logging.getLogger(__name__)


@app.post("/desk/create")
def create_new_desk(
    desk_name: str,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    try:
        desk = create_desk(db=db, desk_name=desk_name)
        db.commit()
        return desk
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/desk/{desk_uuid}")
def get_desk(desk_uuid: str, db: Session = Depends(get_session)):
    try:
        return get_desk_by_uuid(db=db, desk_uuid=desk_uuid)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/desks/")
def list_desks(skip: int = 0, limit: int = 10, db: Session = Depends(get_session)):
    try:
        return get_all_desks(db=db, skip=skip, limit=limit)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/desk/update/{desk_uuid}")
def modify_desk(desk_uuid: str, desk_name: str, db: Session = Depends(get_session)):
    try:
        desk = update_desk(db=db, desk_uuid=desk_uuid, desk_name=desk_name)
        db.commit()
        return desk
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/desk/delete/{desk_uuid}")
def remove_desk(desk_uuid: str, db: Session = Depends(get_session)):
    try:
        result = delete_desk(db=db, desk_uuid=desk_uuid)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
