from app.extension.emun_setting import OrderStatusEnum

# 訂單狀態對照表，方便測試使用
ORDER_STATUS = {
    "pending": OrderStatusEnum.PENDING.value,
    "cooking": OrderStatusEnum.COOKING.value,
    "completed": OrderStatusEnum.COMPLETED.value,
    "cancelled": OrderStatusEnum.CANCELLED.value,
}


# 訂單狀態檢查函數
def is_order_pending(status):
    """檢查訂單是否為pending狀態"""
    return status == OrderStatusEnum.PENDING.value


def is_order_completed(status):
    """檢查訂單是否為completed狀態"""
    return status == OrderStatusEnum.COMPLETED.value


def get_status_name(status_code):
    """根據狀態碼獲取狀態名稱"""
    for name, code in ORDER_STATUS.items():
        if code == status_code:
            return name
    return "unknown"
