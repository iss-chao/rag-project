from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user_role import create_user_role, get_user_role, get_user_role_list, update_user_role, get_user_role_by_id, delete_user_role

async def create_user_role_service(db: AsyncSession, payload: dict):
  # 查看是否存在该用户角色
  user_role = await get_user_role(db, payload["user_id"], payload["role_id"])
  if user_role is not None:
    raise HTTPException(400, "用户已存在")
  await create_user_role(db, payload)
  return "添加成功"


async def get_user_role_list_service(db: AsyncSession,page_query):
  return await get_user_role_list(db, page_query)


async def update_user_role_service(db: AsyncSession, user_role_id: int, payload: dict):
  # 查询用户角色是否存在
  user_role = await get_user_role_by_id(db, user_role_id)
  if user_role is None:
    raise HTTPException(400, "用户角色不存在")
  await update_user_role(db, user_role_id,payload)
  return "修改成功"

async def delete_user_role_service(db: AsyncSession, user_role_id: int):
  # 查询用户角色是否存在
  user_role = await get_user_role_by_id(db, user_role_id)
  if user_role is None:
    raise HTTPException(400, "用户角色不存在")
  await delete_user_role(db, user_role_id)
  return "删除成功"