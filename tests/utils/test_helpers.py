from app.extension.redis_utils import (
    generate_verification_code,
    store_verification_code,
    verify_code,
    redis_client,
)
from typing import Optional
import time


class VerificationCodeHelper:
    """驗證碼測試輔助類"""

    @staticmethod
    def create_test_code(email: str, code: Optional[str] = None) -> str:
        """為測試創建驗證碼"""
        if code is None:
            code = generate_verification_code()

        store_verification_code(email, code)
        return code

    @staticmethod
    def get_stored_code(email: str) -> Optional[str]:
        """從 Redis 獲取存儲的驗證碼"""
        return redis_client.get(f"verify:{email}")

    @staticmethod
    def cleanup_test_codes(*emails: str):
        """清理測試驗證碼"""
        for email in emails:
            redis_client.delete(f"verify:{email}")
            redis_client.delete(f"ratelimit:{email}")

    @staticmethod
    def wait_for_rate_limit_reset(email: str, max_wait: int = 10):
        """等待頻率限制重置"""
        for _ in range(max_wait):
            if not redis_client.exists(f"ratelimit:{email}"):
                break
            time.sleep(1)


def complete_customer_verification_flow(
    client, customer_data: dict, desk_uuid: str = None
):
    """完整的顧客驗證流程測試輔助函數"""
    helper = VerificationCodeHelper()

    try:
        # 1. 發送驗證碼
        response = client.post("/custom/email-send-code", json=customer_data)
        assert response.status_code == 200

        # 2. 獲取實際驗證碼
        actual_code = helper.get_stored_code(customer_data["email"])
        assert actual_code is not None, "驗證碼應該已存儲"

        # 3. 根據是否有桌位決定驗證類型
        if desk_uuid:
            # 內用驗證
            verify_data = {
                "email": customer_data["email"],
                "verify_code": actual_code,
                "desk_uuid": desk_uuid,
            }
            verify_response = client.post("/verify/dine-in", json=verify_data)
        else:
            # 外帶驗證
            verify_data = {
                "email": customer_data["email"],
                "verify_code": actual_code,
                "phone": customer_data["phone"],
            }
            verify_response = client.post("/verify/takeout", json=verify_data)

        assert verify_response.status_code == 200
        return verify_response.json()

    finally:
        # 清理測試資料
        helper.cleanup_test_codes(customer_data["email"])
