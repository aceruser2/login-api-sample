import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
import bcrypt

# 添加專案根目錄到 Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 先載入環境變數
from app.extension.loadenv import load

load()

# 再導入其他模組
from app import app
from app.model import Base
from app.config import sqlconn

# 測試資料庫設定
db_url = URL.create(
    drivername=sqlconn.drivername,
    username=sqlconn.username,
    password=sqlconn.password,
    host=sqlconn.host,
    port=sqlconn.port,
    database=sqlconn.database,
)

engine = create_engine(url=db_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """設置測試資料庫"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """提供資料庫會話"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """提供 FastAPI 測試客戶端"""
    return TestClient(app)


@pytest.fixture
def admin_token(db_session, client):
    """提供管理員令牌（確保密碼加密與登入一致）"""
    from app.services.user_service import (
        create_role,
        create_user,
        create_permission,
        create_role_permission,
        get_user_by_username,
    )
    from app.model.user_model import User

    # 檢查是否已存在管理員用戶
    admin_user = get_user_by_username(db=db_session, username="admin")
    if not admin_user:
        # 創建角色
        default_role = create_role(db=db_session, role_name="Admin", level=1)
        # 創建權限
        mock_permission = create_permission(
            db=db_session,
            permission_name="all_access",
            permission_attributes={
                "can_create": True,
                "can_read": True,
                "can_update": True,
                "can_delete": True,
            },
        )
        # 建立角色權限關聯
        create_role_permission(
            db=db_session,
            role_uuid=default_role.uuid,
            permission_uuid=mock_permission.uuid,
        )

        # 直接創建User對象以確保密碼正確處理
        admin_user = User(
            username="admin",
            email="admin@example.com",
            info={"gender": "male", "true_name": "Admin User"},
        )
        # 使用setter設置密碼
        admin_user.password = "123456"

        db_session.add(admin_user)
        db_session.flush()  # 獲取UUID

        # 創建角色關聯
        from app.model.user_model import RoleUser

        role_user = RoleUser(user_uuid=admin_user.uuid, role_uuid=default_role.uuid)
        db_session.add(role_user)

        db_session.commit()
        db_session.refresh(admin_user)
    else:
        # 重設密碼確保一致性
        admin_user.password = "123456"
        db_session.commit()
        db_session.refresh(admin_user)

    # 驗證密碼
    admin_user = get_user_by_username(db=db_session, username="admin")
    assert admin_user is not None
    db_session.refresh(admin_user)

    # 如果密碼驗證仍失敗，強制重建用戶
    if not admin_user.check_password("123456"):
        # 刪除現有用戶
        db_session.delete(admin_user)
        db_session.commit()

        # 重新創建
        admin_user = User(
            username="admin",
            email="admin@example.com",
            info={"gender": "male", "true_name": "Admin User"},
        )
        admin_user.password = "123456"
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)

    # 最終驗證
    assert admin_user.check_password("123456"), "Admin password verification failed"

    # 執行登入取得token
    login_data = {"username": "admin", "password": "123456"}
    response = client.post("/token/staff", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def refresh_token(db_session, client):
    """提供管理員令牌（確保密碼加密與登入一致）"""
    from app.services.user_service import (
        create_role,
        create_user,
        create_permission,
        create_role_permission,
        get_user_by_username,
    )
    from app.model.user_model import User

    # 檢查是否已存在管理員用戶
    admin_user = get_user_by_username(db=db_session, username="admin")
    if not admin_user:
        # 創建角色
        default_role = create_role(db=db_session, role_name="Admin", level=1)
        # 創建權限
        mock_permission = create_permission(
            db=db_session,
            permission_name="all_access",
            permission_attributes={
                "can_create": True,
                "can_read": True,
                "can_update": True,
                "can_delete": True,
            },
        )
        # 建立角色權限關聯
        create_role_permission(
            db=db_session,
            role_uuid=default_role.uuid,
            permission_uuid=mock_permission.uuid,
        )

        # 直接創建User對象以確保密碼正確處理
        admin_user = User(
            username="admin",
            email="admin@example.com",
            info={"gender": "male", "true_name": "Admin User"},
        )
        # 使用setter設置密碼
        admin_user.password = "123456"

        db_session.add(admin_user)
        db_session.flush()  # 獲取UUID

        # 創建角色關聯
        from app.model.user_model import RoleUser

        role_user = RoleUser(user_uuid=admin_user.uuid, role_uuid=default_role.uuid)
        db_session.add(role_user)

        db_session.commit()
        db_session.refresh(admin_user)
    else:
        # 重設密碼確保一致性
        admin_user.password = "123456"
        db_session.commit()
        db_session.refresh(admin_user)

    # 驗證密碼
    admin_user = get_user_by_username(db=db_session, username="admin")
    assert admin_user is not None
    db_session.refresh(admin_user)

    # 如果密碼驗證仍失敗，強制重建用戶
    if not admin_user.check_password("123456"):
        # 刪除現有用戶
        db_session.delete(admin_user)
        db_session.commit()

        # 重新創建
        admin_user = User(
            username="admin",
            email="admin@example.com",
            info={"gender": "male", "true_name": "Admin User"},
        )
        admin_user.password = "123456"
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)

    # 最終驗證
    assert admin_user.check_password("123456"), "Admin password verification failed"

    # 執行登入取得token
    login_data = {"username": "admin", "password": "123456"}
    response = client.post("/token/staff", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["refresh_token"]



@pytest.fixture
def mock_user_data():
    """測試用戶資料"""
    return {
        "username": "testuser",
        "password": "Test@1234",
        "email": "testuser@example.com",
        "gender": "male",
        "true_name": "Test User",
        "role_uuid": None,
    }


@pytest.fixture
def mock_customer_data():
    """測試顧客資料"""
    return {
        "custom_name": "Test Customer",
        "phone": "1234567890",
        "desk_uuid": "test-desk-uuid",
    }


@pytest.fixture
def mock_desk_data():
    """測試桌位資料"""
    return {"desk_name": "Table 1"}


@pytest.fixture(scope="session", autouse=True)
def setup_redis():
    """設置測試 Redis"""
    from app.extension.redis_utils import redis_client

    # 測試開始前清理 Redis
    redis_client.flushdb()

    yield

    # 測試結束後清理 Redis
    redis_client.flushdb()


@pytest.fixture(autouse=True)
def cleanup_redis_after_test():
    """每個測試後清理 Redis 中的測試資料"""
    yield

    from app.extension.redis_utils import redis_client

    # 清理所有驗證碼相關的鍵
    keys = redis_client.keys("verify:*") + redis_client.keys("ratelimit:*")
    if keys:
        redis_client.delete(*keys)


@pytest.fixture
def mock_customer_token(db_session):
    """生成模擬內用顧客token（含桌位綁定）"""
    from app.extension.jwt_config import create_access_token
    from datetime import timedelta
    from app.services.custom_service import create_customer
    from app.services.desk_service import create_desk, CreateDeskSchema

    try:
        # 創建測試顧客
        customer = create_customer(
            db=db_session,
            customer_name="Test Dine-in Customer",
            customer_phone="0912345678",
            email="dinein@example.com",
            is_verified=True,
        )

        # 創建測試桌位
        desk_schema = CreateDeskSchema(
            desk_name="Table A1", capacity=4, is_available=True
        )
        desk = create_desk(db=db_session, desk_data=desk_schema)

        db_session.commit()

        # 生成包含桌位信息的token
        customer_data = {
            "sub": customer.uuid,
            "user_type": "customer",
            "desk_uuid": desk.uuid,
            "email": customer.email,
        }

        token = create_access_token(
            data=customer_data, expires_delta=timedelta(hours=1)
        )
        return f"Bearer {token}"

    except Exception:
        db_session.rollback()
        # 如果創建失敗，返回默認token
        default_data = {
            "sub": "customer-uuid-123",
            "user_type": "customer",
            "desk_uuid": "desk-uuid-1",
            "email": "dinein@example.com",
        }
        token = create_access_token(data=default_data, expires_delta=timedelta(hours=1))
        return f"Bearer {token}"


@pytest.fixture
def mock_customer_takeout_token(db_session):
    """生成模擬外帶顧客token（無桌位）"""
    from app.extension.jwt_config import create_access_token
    from datetime import timedelta
    from app.services.custom_service import create_customer

    try:
        # 創建測試外帶顧客
        customer = create_customer(
            db=db_session,
            customer_name="Test Takeout Customer",
            customer_phone="0987654321",
            email="takeout@example.com",
            is_verified=True,
        )

        db_session.commit()

        # 生成外帶顧客token（無桌位信息）
        customer_data = {
            "sub": customer.uuid,
            "user_type": "customer",
            "email": customer.email,
            # 外帶無desk_uuid
        }

        token = create_access_token(
            data=customer_data, expires_delta=timedelta(hours=1)
        )
        return f"Bearer {token}"

    except Exception:
        db_session.rollback()
        # 如果創建失敗，返回默認token
        default_data = {
            "sub": "customer-takeout-uuid-456",
            "user_type": "customer",
            "email": "takeout@example.com",
        }
        token = create_access_token(data=default_data, expires_delta=timedelta(hours=1))
        return f"Bearer {token}"
