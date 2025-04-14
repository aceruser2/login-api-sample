import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from app.adapter.model import Base
from app.extension.sql_ext import session_maker

# Use PostgreSQL for testing
engine = create_engine("postgresql+psycopg2://user:123456@localhost:7000/db")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the database session for tests
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


client = TestClient(app)
# 錯誤處理測試：

# 缺少必要字段
# 重複數據
# 無效的輸入值
# 驗證流程測試：

# 完整的顧客創建和驗證流程
# Token 刷新機制
# 業務邏輯測試：

# 桌位綁定的各種情況
# 用戶權限和角色驗證
# 邊界條件測試：

# 重複操作的處理
# 過期處理
# 無效數據的處理

@pytest.fixture
def admin_token(db_session):
    # Create a default role for testing
    from app.adapter.user import create_role, create_user

    default_role = create_role(db=db_session, role_name="Admin", level=1)

    # Create an admin user for testing
    create_user(
        db=db_session,
        username="admin",
        password="123456",
        email="admin@example.com",
        gender="male",
        true_name="Admin User",
        role_uuid=default_role.uuid,  # Use the created role's UUID
    )
    login_data = {"username": "admin", "password": "123456", "userstatus": 0}
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def mock_user_data():
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
    return {
        "custom_name": "Test Customer",
        "phone": "1234567890",
        "desk_uuid": "test-desk-uuid",
    }

@pytest.fixture
def mock_desk_data():
    return {
        "desk_name": "Table 1"
    }

# User API Tests
def test_create_user(mock_user_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == mock_user_data["username"]

def test_create_user_missing_required_fields(admin_token):
    """Test creating user with missing required fields"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    incomplete_data = {"username": "testuser"}
    response = client.post("/create_user/", json=incomplete_data, headers=headers)
    assert response.status_code == 400

def test_create_user_duplicate_email(mock_user_data, admin_token):
    """Test creating user with duplicate email"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create first user
    client.post("/create_user/", json=mock_user_data, headers=headers)
    # Try creating second user with same email
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 400

def test_create_user_invalid_role(mock_user_data, admin_token):
    """Test creating user with invalid role UUID"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    mock_user_data["role_uuid"] = "invalid-uuid"
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 400

def test_get_user_by_uuid(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "test-user-uuid"
    response = client.get(f"/get_user_by_uuid/?user_uuid={user_uuid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["uuid"] == user_uuid


def test_delete_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "test-user-uuid"
    response = client.delete(f"/delete_user/?user_uuid={user_uuid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["uuid"] == user_uuid

# Login API Tests
def test_login_user(mock_user_data):
    login_data = {
        "username": mock_user_data["username"],
        "password": mock_user_data["password"],
        "userstatus": 0,
    }
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(mock_user_data):
    """Test login with invalid credentials"""
    login_data = {
        "username": mock_user_data["username"],
        "password": "wrongpassword",
        "userstatus": 0
    }
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 401

def test_login_missing_fields():
    """Test login with missing fields"""
    response = client.post("/token/user", json={})
    assert response.status_code == 400

# Customer API Tests
def test_create_customer(mock_customer_data):
    response = client.post("/token/dine-in", json=mock_customer_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_customer_missing_fields():
    """Test creating customer with missing fields"""
    incomplete_data = {"custom_name": "Test"}
    response = client.post("/token/dine-in", json=incomplete_data)
    assert response.status_code == 400

def test_create_customer_with_verification(mock_customer_data):
    """Test complete customer creation flow with verification"""
    # First step - request verification
    mock_customer_data["email"] = "test@example.com"
    response = client.post("/token/dine-in", json=mock_customer_data)
    assert response.status_code == 200
    assert response.json()["require_verification"] == True
    
    # Second step - verify code
    verification_data = {**mock_customer_data, "verification_code": "123456"}
    response = client.post("/verify/dine-in", json=verification_data)
    assert response.status_code == 400  # Should fail with invalid code

# Desk API Tests
def test_bind_desk(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": mock_customer_data["desk_uuid"],
    }
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["desk_uuid"] == mock_customer_data["desk_uuid"]

def test_get_active_desk_binding(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_phone = mock_customer_data["phone"]
    response = client.get(
        f"/desk-customer/active?customer_phone={customer_phone}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["desk_uuid"] == mock_customer_data["desk_uuid"]

def test_release_desk(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {"customer_phone": mock_customer_data["phone"]}
    response = client.post("/desk-customer/release", json=request_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "desk unbound"

def test_create_desk(mock_desk_data, admin_token):
    """Test desk creation"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/desk/create", json=mock_desk_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["desk_name"] == mock_desk_data["desk_name"]

def test_get_all_desks(admin_token):
    """Test retrieving all desks"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/desks/", headers=headers)
    assert response.status_code == 200
    assert "total" in response.json()
    assert "desks" in response.json()

def test_bind_desk_invalid_desk(mock_customer_data, admin_token):
    """Test binding with invalid desk UUID"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": "invalid-uuid"
    }
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 404

def test_bind_desk_already_bound(mock_customer_data, admin_token):
    """Test binding when customer already has active binding"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": mock_customer_data["desk_uuid"]
    }
    # First binding
    client.post("/desk-customer/", json=request_data, headers=headers)
    # Try second binding
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 400

# Token Refresh Tests
def test_refresh_token(mock_user_data):
    """Test token refresh functionality"""
    # First login to get tokens
    login_data = {
        "username": mock_user_data["username"],
        "password": mock_user_data["password"],
        "userstatus": 0
    }
    login_response = client.post("/token/user", json=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    # Try refreshing token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("/refresh", headers=headers)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_refresh_token_invalid():
    """Test refresh with invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.post("/refresh", headers=headers)
    assert response.status_code == 401
