from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from core.config import settings
from datetime import timedelta
from core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from models.user import User
from schemas.response import ApiResponse
from schemas.auth import UserReqest, RegisterResponse, LoginResponse, UserResponse, RoleUserResponse, UserInfoResponse
from crud.auth import get_user_by_username, user_register, get_user_all, get_user_by_id
from crud.user_role import get_user_role_by_user_id
from core.logger import logger
import json

async def login_service(db: AsyncSession, user_request:UserReqest):
  """用户登录接口：验证用户名密码，返回JWT Token"""
  # 从数据库查询用户
  user_db = await get_user_by_username(db, user_request.username)
  if not user_request or not verify_password(user_request.password, user_db.hashed_password):
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户名或密码错误")

  # 生成JWT Token（包含用户名作为sub）
  access_token = create_access_token(
      data={"sub": str(user_db.id)},  # 这里我们把用户名放在sub字段，方便后续验证Token时获取用户信息
      expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  # 设置Token过期时间
  )

  # 生成Refresh Token（可选，存储在Cookie中）
  refresh_token = create_refresh_token(
      data={"sub": str(user_db.id)},  # 这里我们把用户名放在sub字段，方便后续验证Token时获取用户信息
      expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)  # 设置Token过期时间
  )

  return LoginResponse(
     access_token=access_token,
     refresh_token=refresh_token,
     token_type="bearer",
    #  userinfo={"username": user_request.username, "userid": user_db.id},
    #  user_role=RoleUserResponse.model_validate(user_role)
  )


async def get_user_info_service(db: AsyncSession, user_id: int):
  user_info = await get_user_by_id(db, user_id)
  user_role = await get_user_role_by_user_id(db, user_id)
  return UserInfoResponse(
    user_id=user_info.id,
    username=user_info.username,
    user_role=RoleUserResponse.model_validate(user_role)
  )


async def register_service(db: AsyncSession, user_request: UserReqest):
  """用户注册接口：写入数据库+密码加密"""
  # 检查用户名是否已存在
  existing_user = await get_user_by_username(db, user_request.username)
  if existing_user:
      return ApiResponse(
          code=status.HTTP_400_BAD_REQUEST,
          msg="Username already registered",
          data=None
      )
  
  # 创建新用户对象，密码加密
  new_user = User(
      username=user_request.username,
      hashed_password=get_password_hash(user_request.password)
  )
  logger.info(f"注册新用户: {new_user.username}, 加密密码: {new_user.hashed_password}")
  await user_register(db, new_user)


async def refresh_token_service(refresh_token):
  """通过刷新令牌获取新的访问令牌"""
  try:
      payload: dict = verify_refresh_token(refresh_token)
      id: str = payload["sub"]
      # 生成新的访问令牌
      new_access_token = create_access_token(
          data={"sub": id},
          expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
      )
      return {"access_token": new_access_token, "token_type": "bearer"}
  except JWTError:
      raise HTTPException(status_code=401, detail="无效的刷新令牌")


async def get_users_all_service(db: AsyncSession):
  users = await get_user_all(db)
  return [UserResponse.model_validate(user) for user in users]