from sqlalchemy.ext.asyncio import AsyncSession
from schemas.kb_role import KbRoleResponse
from crud.kb_role import get_kb_role_list

async def get_kb_role_list_service(db: AsyncSession):
  role_list = await get_kb_role_list(db)
  return [KbRoleResponse.model_validate(role) for role in role_list]