from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 創建速率限制器
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Restaurant API", version="1.0.0")

# 添加速率限制中間件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 註冊所有路由
from app.api import (
    customer_api,
    desk_api,
    menu_api,
    order_api,
    payment_api,
    report_api,
    user_api,
    login_api,
)

# 註冊API路由
app.include_router(customer_api.router, prefix="/customers", tags=["customers"])
app.include_router(desk_api.router, prefix="/desk", tags=["desk"])  # 兼容舊路由



