from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app import app
from app.config import JwtEnv
from app.services.user_service import (
    get_user_by_username,
    get_user_all_role_and_permission_by_user_uuid,
)
from app.services.custom_service import (
    get_customer_by_email,
    create_customer,
    create_desk_customer,
    bind_desk_to_customer,
    get_active_binding,
    release_binding,
    update_customer as update_customer_service,
    delete_customer as delete_customer_service,
)
from app.services.desk_service import get_desk_by_uuid
from app.extension.sql_ext import get_session, Session
from app.schema import (
    Token,
    LoginToken,
    LoginData,
    UserData,
    CustomTakeOutVerify,
    CustomLoginData,
    CustomDineVerify,
    DeskBindingRequest,
    DeskBindingResponse,
    ReleaseBindingRequest,
    ReleaseBindingResponse,
)
from app.extension.jwt_config import (
    create_access_token,
    create_refresh_token,
    refresh_get_current_user,
    get_current_user,
)
from app.model import User, Role, Permission
from typing import Union, Optional
import logging
from app.extension.redis_utils import (
    generate_verification_code,
    store_verification_code,
    can_send_new_code,
    verify_code,
)
from app.services.email_service import send_verification_email

log = logging.getLogger(__name__)


def generate_staff_tokens(user_uuid: str, extra_data: dict = None):
    """
    生成員工JWT令牌（訪問令牌和刷新令牌）

    Args:
        user_uuid (str): 員工UUID
        extra_data (dict, optional): 額外需要包含在令牌中的數據

    Returns:
        tuple: (access_token, refresh_token) 訪問令牌和刷新令牌
    """
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_uuid, "user_type": "staff", **(extra_data or {})},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user_uuid},
        expires_delta=access_token_expires,
    )
    return access_token, refresh_token


def generate_custom_tokens(custom_uuid: str, extra_data: dict = None):
    """
    生成顧客JWT令牌（訪問令牌和刷新令牌）

    Args:
        custom_uuid (str): 顧客UUID
        extra_data (dict, optional): 額外需要包含在令牌中的數據

    Returns:
        tuple: (access_token, refresh_token) 訪問令牌和刷新令牌
    """
    access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": custom_uuid, "user_type": "customer" ** (extra_data or {})},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": custom_uuid},
        expires_delta=access_token_expires,
    )
    return access_token, refresh_token


@app.post("/token/staff")
async def login_staff(
    login_data: LoginData,
    db: Session = Depends(get_session),
) -> LoginToken:
    """
    員工登入端點

    Args:
        login_data (LoginData): 包含使用者名稱和密碼的登入資料
        db (Session): 資料庫連線

    Returns:
        LoginToken: 包含訪問令牌和刷新令牌的響應

    Raises:
        HTTPException: 當登入失敗時
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
            # 處理用戶角色權限資料
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
        access_token, refresh_token = generate_staff_tokens(user.uuid, extra_data)

        log.info(f"User {user.username} logged in successfully")

        return LoginToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        log.critical(
            f"Login failed for user {login_data.username}: {e} {e.__traceback__.tb_lineno}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh/staff")
def refresh_staff(
    db: Session = Depends(get_session),
    refresh_get_current_user: User = Depends(refresh_get_current_user),
) -> Token:
    """
    刷新員工訪問令牌

    Args:
        db (Session): 資料庫連線
        refresh_get_current_user (User): 從刷新令牌獲取的當前使用者

    Returns:
        Token: 包含新訪問令牌的響應
    """
    try:
        access_token, _ = generate_staff_tokens(refresh_get_current_user)
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        log.critical(f"Token refresh failed: {str(e)}", exc_info=True)
        raise e


@app.post("/custom/email-send-code")
async def login_dine_in_customer(
    login_data: CustomLoginData,
    db: Session = Depends(get_session),
) -> dict:
    """
    顧客登入第一步 - 發送電子郵件驗證碼

    Args:
        login_data (CustomLoginData): 包含姓名、電話和電子郵件的顧客資料
        db (Session): 資料庫連線

    Returns:
        dict: 包含驗證結果和顧客狀態的響應

    Raises:
        HTTPException: 當發送失敗或請求過於頻繁時
    """
    try:
        # Check if user exists
        user = get_customer_by_email(db, login_data.email)
        new_user = False
        if user and user.customer_phone != login_data.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number does not match the existing account",
            )
        elif not user:
            user = create_customer(
                db=db,
                customer_name=login_data.custom_name,
                customer_phone=login_data.phone,
                email=login_data.email,
                is_verified=False,
            )
            new_user = True
            db.commit()
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
            "is_new_user": new_user,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log.critical(f"Email verification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code",
        )


@app.post("/verify/dine-in", response_model=LoginToken)
def verify_dine_in(
    verification_data: CustomDineVerify, db: Session = Depends(get_session)
):
    """內用驗證"""
    try:
        # 驗證碼驗證
        if not verify_code(verification_data.email, verification_data.verify_code):
            raise HTTPException(
                status_code=400, detail="Invalid or expired verification code"
            )

        # Create or get user
        user = get_customer_by_email(db, verification_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user and user.is_verified == False:
            user.is_verified = True
            db.commit()
        # Verify and bind desk
        desk = get_desk_by_uuid(db, verification_data.desk_uuid)
        if not desk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Desk not found"
            )

        # Check active binding - 增加註解說明綁定有效期為1小時
        active_binding = get_active_binding(db, verification_data.email)
        if active_binding and active_binding.create_dt + timedelta(
            hours=1
        ) > datetime.now(timezone.utc):
            # 如果已有未過期的綁定（1小時內），則拒絕新的綁定
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer already has an active desk binding (valid for 1 hour)",
            )

        # Bind desk and generate tokens
        desk_to_customer = bind_desk_to_customer(
            db, verification_data.email, verification_data.desk_uuid
        )
        db.commit()
        desk_uuid = desk_to_customer.desk_uuid
        extra_data = {"desk_uuid": desk_uuid}
        access_token, refresh_token = generate_custom_tokens(
            user.uuid, extra_data={"desk_uuid": desk_uuid}
        )

        return LoginToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise e


@app.post("/verify/takeout")
async def verify_takeout(
    login_data: CustomTakeOutVerify,
    db: Session = Depends(get_session),
) -> LoginToken:
    """
    外帶顧客驗證碼確認

    Args:
        login_data (CustomTakeOutVerify): 包含電子郵件和驗證碼的資料
        db (Session): 資料庫連線

    Returns:
        LoginToken: 包含訪問令牌和刷新令牌的響應

    Raises:
        HTTPException: 當驗證失敗時
    """
    try:
        if not verify_code(login_data.email, login_data.verify_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code",
            )
        user = get_customer_by_email(db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user and user.is_verified == False:
            user.is_verified = True
            db.commit()
        access_token, refresh_token = generate_custom_tokens(user.uuid, {})
        print(access_token, refresh_token)
        return LoginToken(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise e


@app.post("/desk-customer/", response_model=DeskBindingResponse)
def bind_desk(
    request: DeskBindingRequest,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    綁定顧客與桌位 - 員工操作或顧客自助
    """
    try:
        # 檢查現有綁定
        try:
            active_binding = get_active_binding(db, request.customer_email)
            if active_binding and active_binding.create_dt + timedelta(
                hours=1
            ) > datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer already has an active desk binding",
                )
        except ValueError:
            # 沒有現有綁定，可以繼續
            pass

        # 驗證桌位是否存在
        desk = get_desk_by_uuid(db, request.desk_uuid)
        if not desk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Desk not found"
            )

        binding = bind_desk_to_customer(db, request.customer_email, request.desk_uuid)
        db.commit()
        return DeskBindingResponse(
            desk_uuid=binding.desk_uuid,
            customer_uuid=binding.customer_uuid,
            create_dt=binding.create_dt,
        )
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/desk-customer/active", response_model=DeskBindingResponse)
def get_active_desk_binding(customer_email: str, db: Session = Depends(get_session)):
    """
    獲取顧客活躍的桌位綁定（1小時內）

    Args:
        customer_email (str): 顧客電子郵件
        db (Session): 資料庫連線

    Returns:
        DeskBindingResponse: 活躍的桌位綁定

    Raises:
        HTTPException: 當找不到活躍的桌位綁定時
    """
    binding = get_active_binding(db, customer_email)
    # 檢查是否存在綁定且未過期（1小時有效期）
    if not binding or binding.create_dt + timedelta(hours=1) <= datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active desk binding found or binding has expired (1 hour limit)",
        )
    return DeskBindingResponse(
        desk_uuid=binding.desk_uuid,
        customer_uuid=binding.customer_uuid,
        create_dt=binding.create_dt,
    )


@app.post("/desk-customer/release", response_model=ReleaseBindingResponse)
def release_desk(request: ReleaseBindingRequest, db: Session = Depends(get_session)):
    """
    釋放顧客的桌位綁定

    Args:
        request (ReleaseBindingRequest): 包含顧客電子郵件的請求
        db (Session): 資料庫連線

    Returns:
        ReleaseBindingResponse: 釋放結果

    Raises:
        HTTPException: 當找不到活躍的桌位綁定時
    """
    binding = get_active_binding(db, request.customer_email)
    if not binding or binding.create_dt + timedelta(hours=1) <= datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active desk binding to release",
        )
    release_result = release_binding(db, request.customer_email)
    return ReleaseBindingResponse(message=release_result["message"])


@app.put("/customer/update")
def update_customer_api(
    customer_uuid: str,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    db: Session = Depends(get_session),
):
    """
    更新顧客資訊

    Args:
        customer_uuid (str): 顧客UUID
        customer_name (str, optional): 新的顧客姓名
        customer_phone (str, optional): 新的顧客電話
        db (Session): 資料庫連線

    Returns:
        Customer: 更新後的顧客資訊

    Raises:
        HTTPException: 當更新失敗時
    """
    try:
        return update_customer_service(
            db=db,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            customer_phone=customer_phone,
        )
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail="update customer error")


@app.delete("/customer/delete")
def delete_customer_api(customer_uuid: str, db: Session = Depends(get_session)):
    """
    刪除顧客（軟刪除）

    Args:
        customer_uuid (str): 顧客UUID
        db (Session): 資料庫連線

    Returns:
        Customer: 被刪除的顧客資訊

    Raises:
        HTTPException: 當刪除失敗時
    """
    try:
        return delete_customer_service(db=db, customer_uuid=customer_uuid)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail="delete customer error")
    """
    刪除顧客（軟刪除）

    Args:
        customer_uuid (str): 顧客UUID
        db (Session): 資料庫連線

    Returns:
        Customer: 被刪除的顧客資訊

    Raises:
        HTTPException: 當刪除失敗時
    """
    try:
        return delete_customer_service(db=db, customer_uuid=customer_uuid)
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail="delete customer error")
