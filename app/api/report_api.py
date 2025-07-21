from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import app
from app.services.report_service import get_daily_sales, get_popular_items
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.utils.permission_checker import PermissionChecker
import logging
from typing import Tuple

log = logging.getLogger(__name__)


@app.get("/reports/daily-sales")
async def daily_sales_report(
    date: datetime = None,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取日銷售報表（需要報表查看權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "report_management", "can_read"
    )
    try:
        if not date:
            date = datetime.now()
        return get_daily_sales(db=db, date=date)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reports/popular-items")
async def popular_items_report(
    days: int = 7,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """獲取熱門商品報表（需要報表查看權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "report_management", "can_read"
    )
    try:
        return get_popular_items(db=db, days=days)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
