from fastapi import Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import app
from app.adapter.report import get_daily_sales, get_popular_items
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user


@app.get("/reports/daily-sales")
async def daily_sales_report(
    date: datetime = None,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if not date:
        date = datetime.now()
    return get_daily_sales(db=db, date=date)


@app.get("/reports/popular-items")
async def popular_items_report(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return get_popular_items(
        db=db, start_date=start_date, end_date=end_date, limit=limit
    )
