from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime

from app.adapter.model import Payment, Order, DeskCustomer
from app.adapter.schema import PaymentCreate
from app.adapter.custom import release_binding
from app.extension.emun_setting import OrderStatusEnum


def create_payment(db: Session, payment: PaymentCreate):
    """Process payment and close order"""
    try:
        # 檢查訂單
        order = db.execute(
            select(Order).where(
                Order.uuid == payment.order_uuid, Order.soft_delete == False
            )
        ).scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == OrderStatusEnum.COMPLETED.value:
            raise HTTPException(status_code=400, detail="Order already completed")

        if payment.amount_paid < order.total_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient payment amount. Required: {order.total_amount}, Provided: {payment.amount_paid}",
            )

        # 建立支付紀錄
        new_payment = Payment(
            order_uuid=payment.order_uuid,
            payment_method=payment.payment_method,
            amount_paid=payment.amount_paid,
            payment_note=payment.payment_note,
        )
        db.add(new_payment)

        # 更新訂單狀態
        order.status = OrderStatusEnum.COMPLETED.value
        order.update_dt = datetime.now()

        # 如果是內用訂單,解除桌位綁定
        if order.desk_uuid:
            desk_binding = db.execute(
                select(DeskCustomer).where(
                    DeskCustomer.desk_uuid == order.desk_uuid,
                    DeskCustomer.customer_uuid == order.customer_uuid,
                    DeskCustomer.soft_delete == False,
                )
            ).scalar_one_or_none()

            if desk_binding:
                desk_binding.soft_delete = True
                desk_binding.update_dt = datetime.now()

        db.commit()
        return new_payment

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
