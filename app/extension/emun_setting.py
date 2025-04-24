from enum import Enum


class UserStatusEnum(Enum):
    STAFF = 0  # 員工
    DESK = 1  # 內用顧客
    CUSTOMER = 2  # 外帶顧客
    DELIVERY = 3  # 外送員
    ADMIN = 4  # 管理員


class OrderStatusEnum(Enum):
    PENDING = 0
    COOKING = 1
    COMPLETED = 2
    CANCELLED = 3


class StockTypeEnum(Enum):
    PURCHASE = 0  # 採購
    CONSUMPTION = 1  # 消耗
    LOSS = 2  # 損耗
