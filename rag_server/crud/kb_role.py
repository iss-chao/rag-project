from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.kb_role import KbRole

async def get_kb_role_list(db: AsyncSession):
  stmt = select(KbRole)
  return await db.scalars(stmt)