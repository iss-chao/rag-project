from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.role import Role

async def get_role_list(db: AsyncSession):
  stmt = select(Role)
  return await db.scalars(stmt)