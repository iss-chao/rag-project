from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_async_db
from models.user import User
from core.security import get_current_user
from crud.user_role import get_user_role_by_user_id


async def require_kb(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  user_role = await get_user_role_by_user_id(db, current_user.id)
  if user_role is None:
    raise HTTPException(status_code=403, detail="没有权限，该用户未分配角色")
  if user_role.role.role_code == 'admin' or user_role.role.role_code == 'user': 
    return
  # raise HTTPException(status_code=403, detail="没有权限，访客不能新建/修改知识库")


async def require_user_role(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  user_role = await get_user_role_by_user_id(db, current_user.id)
  if user_role is None:
    raise HTTPException(status_code=403, detail="没有权限，该用户未分配角色")
  if user_role.role.role_code == 'admin': 
    return
  raise HTTPException(status_code=403, detail="没有权限，该用户不能访问用户权限")