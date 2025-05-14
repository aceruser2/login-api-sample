from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, status, APIRouter
from app import app
from app.config import JwtEnv
from app.adapter.user import (
    get_user_by_username,
    get_user_all_role_and_permission_by_user_uuid,
)
from app.adapter.custom import (
    get_customer_by_email,
    create_customer,
    create_desk_customer,
    bind_desk_to_customer,
    get_active_binding,
    release_binding,
)
from app.adapter.desk import get_desk_by_uuid
from app.extension.sql_ext import get_session, Session
from app.adapter.schema import (
    Token,
    LoginToken,
    LoginData,
    UserData,
    CustomLoginData,
    DeskBindingRequest,
    DeskBindingResponse,
    ReleaseBindingRequest,
    ReleaseBindingResponse,
)
from app.extension.jwt_config import create_access_token, create_refresh_token
from app.adapter.model import User, Role, Permission
from app.extension.jwt_config import refresh_get_current_user
from typing import Union, Optional
import logging

log = logging.getLogger(__name__)

from app.extension.redis_utils import (
    generate_verification_code,
    store_verification_code,
    can_send_new_code,
    verify_code,
)
from app.services.email_service import send_verification_email


def generate_tokens(user_uuid: str, extra_data: dict = None):
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_uuid, **(extra_data or {})},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user_uuid},
        expires_delta=access_token_expires,
    )
    return access_token, refresh_token


@app.post("/token/user")
async def login_user(
    login_data: LoginData,
    db: Session = Depends(get_session),
) -> LoginToken:
    """Standard user login
    test ok
    {
        "access_token": "dfsd",
        "refresh_token": "sdf",
        "token_type": "bearer"
    }
    Authenticates a user and returns access & refresh tokens with role/permission info
    """
    try:
        # Validate input
        if not login_data.username or not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required",
            )

        # Get and verify user
        user = get_user_by_username(db, login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.check_password(login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user's roles and permissions
        all_user_role: list[tuple[User, Role, Permission]] = (
            get_user_all_role_and_permission_by_user_uuid(db, user.uuid)
        )
        if not all_user_role:
            log.warning(f"User {user.username} has no roles/permissions assigned")

        # Extract role and permission data
        extra_data = {"roles": [], "roles_permissions": []}
        log.info(all_user_role)
        if all_user_role:
            # Assuming roles_permissions contains RoleUser objects with relationships
            for user, role, permission in all_user_role:
                if role and permission:
                    role_data = {
                        "role_uuid": role.uuid,
                        "role_name": role.role_name,
                        "level": role.level,
                        "permission_uuid": permission.uuid,
                        "permission_name": permission.permission_name,
                        "attributes": permission.permission_attributes,
                    }
                    extra_data["roles_permissions"].append(role_data)

        # Generate tokens
        access_token, refresh_token = generate_tokens(user.uuid, extra_data)

        log.info(f"User {user.username} logged in successfully")

        return LoginToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(
            f"Login failed for user {login_data.username}: {e} {e.__traceback__.tb_lineno}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during login",
        )


@app.post("/token/dine-in")
async def login_dine_in_customer(
    login_data: CustomLoginData,
    db: Session = Depends(get_session),
) -> dict:
    """Dine-in customer login first step - email verification"""
    try:
        # Check if user exists
        user = get_customer_by_email(db, login_data.email)

        if not can_send_new_code(login_data.email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait 5 minutes before requesting a new code",
            )

        # Generate and store verification code
        code = generate_verification_code()
        store_verification_code(login_data.email, code)

        # Send verification email
        await send_verification_email(login_data.email, code)

        return {
            "message": "Verification code sent",
            "require_verification": True,
            "is_new_user": user is None,
        }

    except Exception as e:
        log.error(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code",
        )


@app.post("/verify/dine-in")
async def verify_dine_in(
    login_data: CustomLoginData,
    verification_code: str,
    db: Session = Depends(get_session),
) -> LoginToken:
    """Complete dine-in login after verification"""
    if not verify_code(login_data.email, verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    # Create or get user
    user = get_customer_by_phone(db, login_data.phone)
    if not user:
        user = create_customer(
            db=db,
            customer_name=login_data.custom_name,
            customer_phone=login_data.phone,
            email=login_data.email,
        )

    # Verify and bind desk
    desk = get_desk_by_uuid(db, login_data.desk_uuid)
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Desk not found"
        )

    # Check active binding
    active_binding = get_active_binding(db, login_data.phone)
    if (
        active_binding
        and active_binding.create_dt + timedelta(hours=1) > datetime.utcnow()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has an active desk binding",
        )

    # Bind desk and generate tokens
    bind_desk_to_customer(db, login_data.phone, login_data.desk_uuid)
    access_token, refresh_token = generate_tokens(user.uuid)

    return LoginToken(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/token/takeout")
async def login_takeout_customer(
    login_data: CustomLoginData,
    db: Session = Depends(get_session),
) -> dict:
    """Takeout customer login first step - email verification"""
    try:
        user = get_customer_by_phone(db, login_data.phone)

        if not can_send_new_code(login_data.email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please wait 5 minutes before requesting a new code",
            )

        code = generate_verification_code()
        store_verification_code(login_data.email, code)
        await send_verification_email(login_data.email, code)

        return {
            "message": "Verification code sent",
            "require_verification": True,
            "is_new_user": user is None,
        }

    except Exception as e:
        log.error(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code",
        )


@app.post("/verify/takeout")
async def verify_takeout(
    login_data: CustomLoginData,
    verification_code: str,
    db: Session = Depends(get_session),
) -> LoginToken:
    """Complete takeout login after verification"""
    if not verify_code(login_data.email, verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    user = get_customer_by_phone(db, login_data.phone)
    if not user:
        user = create_customer(
            db=db,
            customer_name=login_data.custom_name,
            customer_phone=login_data.phone,
            email=login_data.email,
        )

    access_token, refresh_token = generate_tokens(user.uuid)
    return LoginToken(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@app.post("/refresh")
def refresh(
    db: Session = Depends(get_session),
    refresh_get_current_user: User = Depends(refresh_get_current_user),
) -> Token:
    access_token, _ = generate_tokens(refresh_get_current_user)
    return Token(access_token=access_token, token_type="bearer")


@app.post("/desk-customer/", response_model=DeskBindingResponse)
def bind_desk(request: DeskBindingRequest, db: Session = Depends(get_session)):
    """Bind a desk to a customer"""
    active_binding = get_active_binding(db, request.customer_phone)
    if (
        active_binding
        and active_binding.create_dt + timedelta(hours=1) > datetime.utcnow()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer already has an active desk binding",
        )
    binding = bind_desk_to_customer(db, request.customer_phone, request.desk_uuid)
    return DeskBindingResponse(
        desk_uuid=binding.desk_uuid,
        customer_uuid=binding.customer_uuid,
        create_dt=binding.create_dt,
    )


@app.get("/desk-customer/active", response_model=DeskBindingResponse)
def get_active_desk_binding(customer_phone: str, db: Session = Depends(get_session)):
    """Retrieve active desk binding for a customer"""
    binding = get_active_binding(db, customer_phone)
    if not binding or binding.create_dt + timedelta(hours=1) <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active desk binding found",
        )
    return DeskBindingResponse(
        desk_uuid=binding.desk_uuid,
        customer_uuid=binding.customer_uuid,
        create_dt=binding.create_dt,
    )


@app.post("/desk-customer/release", response_model=ReleaseBindingResponse)
def release_desk(request: ReleaseBindingRequest, db: Session = Depends(get_session)):
    """Release desk binding for a customer"""
    binding = get_active_binding(db, request.customer_phone)
    if not binding or binding.create_dt + timedelta(hours=1) <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active desk binding to release",
        )
    release_result = release_binding(db, request.customer_phone)
    return ReleaseBindingResponse(message=release_result["message"])


@app.put("/customer/update")
def update_customer(
    customer_uuid: str,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    db: Session = Depends(get_session),
):
    """更新顧客資訊"""
    try:
        return update_customer(
            db=db,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            customer_phone=customer_phone,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="update customer error")


@app.delete("/customer/delete")
def delete_customer(customer_uuid: str, db: Session = Depends(get_session)):
    """刪除顧客"""
    try:
        return delete_customer(db=db, customer_uuid=customer_uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail="delete customer error")
