from sqlalchemy.ext.asyncio import AsyncSession
from schemas.role import RoleResponse
from crud.role import get_role_list

async def get_role_list_service(db: AsyncSession):
  role_list = await get_role_list(db)
  return [RoleResponse.model_validate(role) for role in role_list]