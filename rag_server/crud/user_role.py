from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from schemas.response import PageQuery, ListDataResponse
from sqlalchemy import func
from models.user_role import UserRole
from schemas.user_role import UserListResponse

async def create_user_role(db: AsyncSession, payload: dict):
  user_role = UserRole(**payload)
  db.add(user_role)
  await db.commit()
  await db.refresh(user_role)
  return user_role


async def get_user_role(db: AsyncSession, user_id: int, role_id: int):
  user_role = await db.scalar(select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id))
  return user_role

async def get_user_role_by_user_id(db: AsyncSession, user_id: int):
  stmt = select(UserRole).where(UserRole.user_id == user_id).options(selectinload(UserRole.role), selectinload(UserRole.user))
  user_role = await db.scalar(stmt)
  return user_role

async def get_user_role_by_id(db: AsyncSession, user_role_id: int):
  user_role = await db.scalar(select(UserRole).where(UserRole.id == user_role_id))
  return user_role

async def get_user_role_list(
  db: AsyncSession,
  page_query: PageQuery,
):
  """获取用户角色列表"""
  # 只允许这些字段排序
  allow_sort_by_fields = ["id", "user_id", "role_id"]
  if page_query.sort_by not in allow_sort_by_fields:
    page_query.sort_by = "id"

  # 设置动态排序
  order_column = getattr(UserRole, page_query.sort_by)
  if page_query.sort_order == "asc":
    order_expr = order_column.asc()
  else:
    order_expr = order_column.desc()

  # 查询数据
  stmt = select(UserRole)\
    .options(
      selectinload(UserRole.user),
      selectinload(UserRole.role)
    )\
    .order_by(order_expr)\
    .limit(page_query.page_size)\
    .offset((page_query.page_num - 1) * page_query.page_size)
  user_roles_orm = await db.execute(stmt)
  user_roles = user_roles_orm.scalars().all()

  # 查询总条数
  total = await db.scalar(select(func.count(UserRole.id)))

  return ListDataResponse(
    items=[UserListResponse.model_validate(user_role) for user_role in user_roles],
    total=total,
    page_query=page_query
  )

async def update_user_role(db: AsyncSession, user_role_id: int, payload: dict):
  user_role = await db.get(UserRole, user_role_id)
  for key, value in payload.items():
    if value is not None:
      setattr(user_role, key, value)
  await db.commit()
  await db.refresh(user_role)
  return user_role


async def delete_user_role(db: AsyncSession, user_role_id: int):
  user_role = await db.get(UserRole, user_role_id)
  await db.delete(user_role)
  await db.commit()