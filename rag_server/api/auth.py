from fastapi import APIRouter,Depends,HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_async_db
from models.user import User
from core.security import oauth2_scheme_from_cookie,get_current_user
from core.config import settings
from datetime import timedelta
from schemas.response import ApiResponse
from schemas.auth import UserReqest, RegisterResponse, LoginResponse, UserResponse, UserInfoResponse
from service.auth import register_service, login_service, refresh_token_service, get_users_all_service, get_user_info_service


router = APIRouter(tags=["用户管理"], prefix="/api/auth")


@router.post("/register", response_model=ApiResponse[RegisterResponse], status_code=status.HTTP_201_CREATED)
async def register(user_request: UserReqest, db: AsyncSession = Depends(get_async_db)):
    # """用户注册接口：写入数据库+密码加密"""
    await register_service(db, user_request)
    return ApiResponse(
        data=RegisterResponse(content="注册成功", username=user_request.username)
    )

@router.post("/login", response_model=ApiResponse[LoginResponse])
async def login(response: Response, user_request: UserReqest, db: AsyncSession = Depends(get_async_db)):
    login_info = await login_service(db, user_request)
    response.set_cookie(
        key="refresh_token",
        value=login_info.refresh_token,
        httponly=True,       # JS不能读取，安全防XSS
        secure=False,        # 本地调试False；线上https改为True
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    return ApiResponse(data=login_info)

# 2. 刷新令牌接口
@router.post("/refresh-token")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme_from_cookie)):  # 自定义从Cookie获取令牌
    refresh_token_info = await refresh_token_service(refresh_token)
    return ApiResponse(data=refresh_token_info)

# 3. 登出接口（清除Cookie）
@router.post("/logout")
async def logout(response: Response):
    """登出：清除刷新令牌Cookie"""
    response.delete_cookie("refresh_token")
    return {"detail": "登出成功"}


@router.get("/info", response_model=ApiResponse[UserInfoResponse])
async def get_user_info(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    """示例：获取当前登录用户信息（必须带Token访问）"""
    user_info = await get_user_info_service(db, current_user.id)
    return ApiResponse(data=user_info)


@router.get("/all", response_model=ApiResponse[list[UserResponse]])
async def read_users_all(db: AsyncSession = Depends(get_async_db)):
    users =  await get_users_all_service(db)
    return ApiResponse(data=users)