from app.adapter.sql_crud import get_user_info


def authenticate_user(username: str, password: str):
    """vaild user"""
    user = get_user_info(username)
    if not user:
        return False
    if not user.check_password(password):
        return False
    return user
