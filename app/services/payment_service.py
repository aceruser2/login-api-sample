from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from app.model import Payment, Order, DeskCustomer
from app.schema import PaymentCreate
from app.extension.emun_setting import OrderStatusEnum


def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    """處理支付並關閉訂單"""
    # 檢查訂單
    stmt = select(Order).where(
        Order.uuid == payment.order_uuid, Order.soft_delete == False
    )
    order = db.execute(stmt).scalar_one_or_none()

    if not order:
        raise ValueError("Order not found")

    if order.status == OrderStatusEnum.COMPLETED.value:
        raise ValueError("Order already completed")

    if payment.amount_paid < order.total_amount:
        raise ValueError("Insufficient payment amount")

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
        binding_stmt = select(DeskCustomer).where(
            DeskCustomer.desk_uuid == order.desk_uuid,
            DeskCustomer.customer_uuid == order.customer_uuid,
            DeskCustomer.soft_delete == False,
        )
        desk_binding = db.execute(binding_stmt).scalar_one_or_none()

        if desk_binding:
            desk_binding.soft_delete = True
            desk_binding.update_dt = datetime.now()

    return new_payment
