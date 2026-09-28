# 加密、JWT工具（新增）
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from core.config import settings
from database_async import get_async_db
from models.user import User
from crud.auth import get_user_by_id
import hashlib

# 密码加密上下文（bcrypt算法）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置（用openssl rand -hex 32生成SECRET_KEY，别用默认值！）


# OAuth2标准验证（从请求头提取Bearer令牌）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def _prehash_password(password: str) -> str:
    """预哈希：用 SHA-256 处理原始密码，生成固定长度摘要"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()  # 取前8字节，适合 bcrypt 长度限制

def get_password_hash(password: str) -> str:
    """先预哈希，再用 bcrypt 加盐哈希（解决长度限制问题）"""
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证时同样先预哈希，再比对 bcrypt 哈希"""
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        data: 要存储在令牌中的数据（如用户ID、用户名）
        expires_delta: 自定义过期时间（None时使用默认配置）
    
    Returns:
        生成的 JWT 令牌字符串
    """
    # 复制数据以避免修改原始字典
    to_encode = data.copy()  # {"sub": "username"}
    
    # 设置过期时间（必须使用 UTC 时间！）
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加过期声明（JWT标准字段）settings
    to_encode.update({"exp": expire})
    
    # 生成并返回 JWT 令牌
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    验证 JWT 令牌并获取用户信息
    
    Args:
        token: 从请求头获取的 JWT 令牌
        credentials_exception: 验证失败时抛出的异常
        db: 数据库会话，用于查询用户信息
    
    Returns:
        验证成功的用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份凭证",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # 解析令牌（验证签名+过期时间）
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception

        # 检查令牌是否过期（JWT库会自动验证exp，但可额外检查）
        # exp = payload.get("exp")
        # if exp is not None and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已过期")
        
        return payload  # 返回令牌中包含的用户信息（如用户名、用户ID等）
    except JWTError:
        raise credentials_exception
    

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> User:
    """获取当前登录用户（依赖注入）"""
    payload = verify_token(token)  # 验证令牌并获取用户信息
    id: str = payload.get("sub")  # 获取用户名
    user = await get_user_by_id(db, int(id))  # 从数据库查询用户对象
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user  # 返回当前登录用户对象


# 从 Cookie 中读取 refresh_token
def oauth2_scheme_from_cookie(request: Request) -> str:
  #  从 Cookie 里拿刷新令牌
  refresh_token = request.cookies.get("refresh_token")
  if not refresh_token:
    raise HTTPException(status_code=4001, detail="缺少刷新令牌")
  return refresh_token




def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建 Refresh Token（专用，区分access token）"""
    to_encode = data.copy()
    # 标记令牌类型：refresh / access（核心区分）
    to_encode.update({"type": "refresh"})
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Dict:
    """专用验证 Refresh Token（禁止用这个验证access token）"""
    
    credentials_exception = HTTPException(
        status_code=4001,
        detail="无效的刷新令牌",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id: int = payload.get("sub")
        token_type: str = payload.get("type")

        # 强制校验：必须是 refresh token
        if id is None or token_type != "refresh":
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception
    