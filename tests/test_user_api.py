import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app

client = TestClient(app)


def test_get_current_user_info(client, admin_token):
    """測試獲取當前用戶信息"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    with patch("app.services.user_service.get_user_by_uuid") as mock_get:
        mock_user = MagicMock()
        mock_user.uuid = "user-uuid-1"
        mock_user.username = "admin"
        mock_get.return_value = mock_user

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "admin"


def test_get_user_info_with_permission(client, admin_token):
    """測試有權限的用戶獲取特定用戶信息"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "user-uuid-2"

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.user_service.get_user_by_uuid") as mock_get:
            mock_user = MagicMock()
            mock_user.uuid = user_uuid
            mock_user.username = "testuser"
            mock_get.return_value = mock_user

            response = client.get(f"/users/{user_uuid}", headers=headers)
            assert response.status_code == 200
            assert response.json()["username"] == "testuser"


def test_get_user_info_without_permission(client, admin_token):
    """測試無權限的用戶獲取特定用戶信息被拒絕"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "user-uuid-3"

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        from fastapi import HTTPException

        mock_perm.side_effect = HTTPException(
            status_code=403, detail="Permission denied"
        )

        response = client.get(f"/users/{user_uuid}", headers=headers)
        assert response.status_code == 403


def test_create_user_with_permission(client, admin_token):
    """測試有權限的用戶創建新用戶"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_data = {
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com",
        "true_name": "New User",
    }

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.user_service.create_user") as mock_create:
            mock_user = MagicMock()
            mock_user.uuid = "new-user-uuid"
            mock_user.username = user_data["username"]
            mock_create.return_value = mock_user

            response = client.post("/create_user/", params=user_data, headers=headers)
            assert response.status_code in [200, 201]


def test_delete_user_with_permission(client, admin_token):
    """測試有權限的用戶刪除用戶"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "user-to-delete-uuid"

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.user_service.delete_user") as mock_delete:
            mock_user = MagicMock()
            mock_user.uuid = user_uuid
            mock_user.soft_delete = True
            mock_delete.return_value = mock_user

            response = client.delete(
                f"/delete_user/?user_uuid={user_uuid}", headers=headers
            )
            assert response.status_code == 200


def test_assign_role_as_admin(client, admin_token):
    """測試管理員分配角色給用戶"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "user-uuid-4"
    role_uuid = "role-uuid-1"

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_admin"
    ) as mock_admin:
        mock_admin.return_value = None

        with patch(
            "app.services.user_service.assign_permission_to_user"
        ) as mock_assign:
            mock_role_user = MagicMock()
            mock_role_user.id = 1
            mock_role_user.user_uuid = user_uuid
            mock_role_user.role_uuid = role_uuid
            mock_assign.return_value = mock_role_user

            response = client.post(
                f"/users/{user_uuid}/assign-role?role_uuid={role_uuid}", headers=headers
            )
            assert response.status_code == 200


def test_assign_role_non_admin(client, admin_token):
    """測試非管理員分配角色給用戶被拒絕"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "user-uuid-5"
    role_uuid = "role-uuid-2"

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_admin"
    ) as mock_admin:
        from fastapi import HTTPException

        mock_admin.side_effect = HTTPException(
            status_code=403, detail="Admin level access required"
        )

        response = client.post(
            f"/users/{user_uuid}/assign-role?role_uuid={role_uuid}", headers=headers
        )
        assert response.status_code == 403


def test_list_all_roles_with_permission(client, admin_token):
    """測試有權限的用戶獲取所有角色"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.user_service.get_all_roles") as mock_get:
            mock_roles = [
                MagicMock(uuid="role-1", role_name="Admin"),
                MagicMock(uuid="role-2", role_name="Staff"),
            ]
            mock_get.return_value = mock_roles

            response = client.get("/roles/", headers=headers)
            assert response.status_code == 200
            assert len(response.json()) == 2
