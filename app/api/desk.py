from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import app
from app.adapter.desk import (
    create_desk,
    get_desk_by_uuid,
    get_all_desks,
    update_desk,
    delete_desk,
)
from app.extension.sql_ext import get_session


@app.post("/desk/create")
def create_new_desk(desk_name: str, db: Session = Depends(get_session)):
    """建立新桌子"""
    try:
        return create_desk(db=db, desk_name=desk_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/desk/{desk_uuid}")
def get_desk(desk_uuid: str, db: Session = Depends(get_session)):
    """取得桌子資訊"""
    try:
        return get_desk_by_uuid(db=db, desk_uuid=desk_uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/desks/")
def list_desks(skip: int = 0, limit: int = 10, db: Session = Depends(get_session)):
    """取得所有桌子"""
    try:
        return get_all_desks(db=db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/desk/update/{desk_uuid}")
def modify_desk(desk_uuid: str, desk_name: str, db: Session = Depends(get_session)):
    """更新桌子資訊"""
    try:
        return update_desk(db=db, desk_uuid=desk_uuid, desk_name=desk_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/desk/delete/{desk_uuid}")
def remove_desk(desk_uuid: str, db: Session = Depends(get_session)):
    """刪除桌子"""
    try:
        return delete_desk(db=db, desk_uuid=desk_uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
