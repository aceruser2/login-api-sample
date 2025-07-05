from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import app
from app.services.report_service import (
    get_daily_sales,
    get_popular_items,
    get_inventory_status,
)
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.schema import DailySalesResponse, PopularItemsResponse, InventoryStatusResponse
import logging

log = logging.getLogger(__name__)


@app.get("/reports/daily-sales", response_model=DailySalesResponse)
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


@app.get("/reports/popular-items", response_model=PopularItemsResponse)
async def popular_items_report(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """獲取熱門商品報表"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        items = get_popular_items(
            db=db, start_date=start_date, end_date=end_date, limit=limit
        )

        # 計算銷售佔比
        total_sales = sum(item["total_sales"] for item in items) if items else 0
        if total_sales > 0:
            for item in items:
                item["percentage_of_sales"] = (item["total_sales"] / total_sales) * 100

        return {
            "period_days": days,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "items": items,
        }
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reports/inventory", response_model=InventoryStatusResponse)
async def inventory_status_report(
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """獲取庫存狀態報表"""
    try:
        return get_inventory_status(db=db)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
