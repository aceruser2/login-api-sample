import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from app import app
from app.adapter.model import Base
from app.extension.sql_ext import session_maker
from app.extension.loadenv import load
from app.config import sqlconn
from app.adapter.user import get_user_by_username

load()
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


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
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


# Fixtures for test data
@pytest.fixture
def admin_token(db_session):
    from app.adapter.user import (
        create_role,
        create_user,
        create_permission,
        create_role_permission,
    )
    admin = get_user_by_username(db=db_session, username="admin")
    if not admin:
        default_role = create_role(db=db_session, role_name="Admin", level=1)

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
        create_role_permission(
            db=db_session,
            role_uuid=default_role.uuid,
            permission_uuid=mock_permission.uuid,
        )

        create_user(
            db=db_session,
            username="admin",
            password="123456",
            email="admin@example.com",
            gender="male",
            true_name="Admin User",
            role_uuid=default_role.uuid,
        )
        db_session.commit()
    login_data = {"username": "admin", "password": "123456"}
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def mock_admin_pass():
    return {
        "username": "admin",
        "password": "123456",
    }


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
    return {"desk_name": "Table 1"}


@pytest.fixture(scope="module")
def mock_menu_item(db_session):
    from app.adapter.model import MenuItem

    item = MenuItem(
        name="測試品項",
        description="自動化測試用",
        price=100,
        category="主餐",
        available=True,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    yield item
    db_session.delete(item)
    db_session.commit()


@pytest.fixture
def mock_order_data(mock_customer_data, mock_menu_item):
    return {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": mock_customer_data["desk_uuid"],
        "items": [
            {
                "item_uuid": mock_menu_item.uuid,
                "quantity": 2,
                "price": mock_menu_item.price,
            }
        ],
    }


# 測試函數已移至 tests/ 目錄下
