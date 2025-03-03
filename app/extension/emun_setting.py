from enum import Enum


class UserStatusEnum(Enum):
    STAFF = 0      # 員工
    DESK = 1       # 內用顧客
    CUSTOMER = 2   # 外帶顧客
    DELIVERY = 3   # 外送員
    ADMIN = 4      # 管理員


