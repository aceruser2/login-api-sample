-- 清除 admin user/role/permission 相關資料（包含關聯表）

-- 關聯表需先刪除，避免外鍵衝突
DELETE FROM role_user WHERE user_uuid IN (SELECT uuid FROM users WHERE username = 'admin');
DELETE FROM role_permission WHERE role_uuid IN (SELECT uuid FROM roles WHERE role_name = 'admin');
DELETE FROM permissions WHERE uuid IN (
    SELECT permission_uuid FROM role_permission WHERE role_uuid IN (SELECT uuid FROM roles WHERE role_name = 'admin')
);
DELETE FROM users WHERE username = 'admin';
DELETE FROM roles WHERE role_name = 'admin';
