from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from starlette.responses import JSONResponse
from app.handler.auth import authenticate_user
from app import app
from app.handler.for_map import auth
from app.config import JwtEnv
from app.adapter import sql_crud


# @app.post("/token")
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         return JSONResponse(status_code=400, content="Incorrect username or password")

#     access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(days=JwtEnv.REFRESH_TOKEN_EXPIRE_DAYS)
#     access_token = Authorize.create_access_token(
#         subject=str(user.uuid),
#         fresh=True,
#         algorithm=JwtEnv.ALGORITHM_LOGIN,
#         expires_time=access_token_expires,
#         user_claims={"username": user.username, "auth_r": list(map(auth, user.auth_r))},
#     )
#     refresh_token = Authorize.create_refresh_token(
#         subject=str(user.uuid),
#         algorithm=JwtEnv.ALGORITHM_REFRESH,
#         expires_time=refresh_token_expires,
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }


# https://indominusbyte.github.io/fastapi-jwt-auth/advanced-usage/dynamic-algorithm/
# In protected route, automatically check incoming JWT
# have algorithm in your `authjwt_decode_algorithms` or not


# @app.post("/refresh")
# def refresh(Authorize: AuthJWT = Depends()):
#     Authorize.jwt_refresh_token_required()

#     current_user = Authorize.get_jwt_subject()
#     user = sql_crud.get_user_by_uuid(current_user)
#     access_token_expires = timedelta(minutes=JwtEnv.ACCESS_TOKEN_EXPIRE_MINUTES)
#     new_access_token = Authorize.create_access_token(
#         subject=str(user.uuid),
#         algorithm=JwtEnv.ALGORITHM_LOGIN,
#         expires_time=access_token_expires,
#         user_claims={"username": user.username, "auth_r": list(map(auth, user.auth_r))},
#     )
#     return {"access_token": new_access_token}
