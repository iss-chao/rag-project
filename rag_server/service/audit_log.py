from sqlalchemy.ext.asyncio import AsyncSession
from crud.audit_log import get_audit_log_list


async def get_audit_log_list_service(db: AsyncSession):
  return await get_audit_log_list(db)