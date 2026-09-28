from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database_async import get_async_db
from schemas.response import ApiResponse
from schemas.kb_role import KbRoleResponse
from service.kb_role import get_kb_role_list_service

router = APIRouter(
  tags=["角色管理"],
  prefix="/api/kb_role"
)

@router.get("/list", response_model=ApiResponse[List[KbRoleResponse]])
async def get_role_list(db: AsyncSession = Depends(get_async_db)):
  role_list = await get_kb_role_list_service(db)
  return ApiResponse(data=role_list)
