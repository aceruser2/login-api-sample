from typing import Dict, Any
from app.extension.emun_setting import OrderStatusEnum
import logging

log = logging.getLogger(__name__)


def get_user_info_from_token(current_user: Any) -> Dict[str, Any]:
    """從JWT token中提取用戶信息"""
    try:
        # 處理不同類型的token payload
        if isinstance(current_user, dict):
            # 直接是token payload
            return {
                "uuid": current_user.get("sub"),
                "user_type": current_user.get("user_type", "staff"),
                "user_status": current_user.get("user_status", 1),
                "desk_uuid": current_user.get("desk_uuid"),
                "email": current_user.get("email"),
            }
        elif hasattr(current_user, 'uuid'):
            # 是用戶對象
            return {
                "uuid": current_user.uuid,
                "user_type": getattr(current_user, "user_type", "staff"),
                "user_status": getattr(current_user, "user_status", 1),
                "desk_uuid": getattr(current_user, "desk_uuid", None),
                "email": getattr(current_user, "email", None),
            }
        else:
            # 可能是字符串UUID
            return {
                "uuid": str(current_user),
                "user_type": "staff",
                "user_status": 1,
                "desk_uuid": None,
                "email": None,
            }
    except Exception as e:
        log.error(f"Error extracting user info from token: {e}")
        return {
            "uuid": None,
            "user_type": "staff",
            "user_status": 1,
            "desk_uuid": None,
            "email": None,
        }


def can_create_order(user_info: Dict[str, Any], order_customer_uuid: str) -> bool:
    """檢查用戶是否可以創建訂單"""
    # 員工可以為任何人創建訂單
    if user_info["user_type"] == "staff" or user_info["user_status"] == 1:
        return True
    
    # 顧客只能為自己創建訂單
    if user_info["user_type"] == "customer" and user_info["user_status"] in [2, 3]:
        return user_info["uuid"] == order_customer_uuid
    
    return False


def can_view_order(user_info: Dict[str, Any], order_customer_uuid: str) -> bool:
    """檢查用戶是否可以查看訂單"""
    # 員工可以查看所有訂單
    if user_info["user_type"] == "staff" or user_info["user_status"] == 1:
        return True
    
    # 顧客只能查看自己的訂單
    if user_info["user_type"] == "customer" and user_info["user_status"] in [2, 3]:
        return user_info["uuid"] == order_customer_uuid
    
    return False


def can_update_order(user_info: Dict[str, Any], order_customer_uuid: str, order_status: int) -> bool:
    """檢查用戶是否可以更新訂單"""
    # 員工可以更新任何訂單
    if user_info["user_type"] == "staff" or user_info["user_status"] == 1:
        return True
    
    # 顧客只能更新自己的pending訂單
    if user_info["user_type"] == "customer" and user_info["user_status"] in [2, 3]:
        return (user_info["uuid"] == order_customer_uuid and 
                order_status == OrderStatusEnum.PENDING.value)
    
    return False


def can_update_order_status(user_info: Dict[str, Any]) -> bool:
    """檢查用戶是否可以更新訂單狀態（僅員工）"""
    return user_info["user_type"] == "staff" or user_info["user_status"] == 1


def filter_orders_by_permission(user_info: Dict[str, Any], orders: list) -> list:
    """根據權限過濾訂單列表"""
    # 員工可以看到所有訂單
    if user_info["user_type"] == "staff" or user_info["user_status"] == 1:
        return orders
    
    # 顧客只能看到自己的訂單
    if user_info["user_type"] == "customer" and user_info["user_status"] in [2, 3]:
        return [order for order in orders if order.customer_uuid == user_info["uuid"]]
    
    return []
