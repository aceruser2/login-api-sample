from fastapi import APIRouter, Depends, HTTPException 
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import app
from app.services.report_service import get_daily_sales, get_popular_items
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
import logging

log = logging.getLogger(__name__)


@app.get("/reports/daily-sales")
async def daily_sales_report(
    date: datetime = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """獲取日銷售報表"""
    try:
        if not date:
            date = datetime.now()
        return get_daily_sales(db=db, date=date)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
