from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database_async import get_async_db
from core.security import get_current_user
from models.user import User
from service.kb_member import get_kb_members_by_id_service, add_kb_member_service, del_kb_member_service, update_kb_member_service
from schemas.response import ApiResponse
from schemas.kb_member import KbMemberResponse, KbMemberRequest, KbMemberUpdateRequest

router = APIRouter(
  tags=["知识库成员"],
  prefix="/api/kb_member",
  dependencies=[Depends(get_current_user)]
)

kb_member_router = APIRouter(
  dependencies=[Depends(get_current_user)]
)

@kb_member_router.get("/list/{kb_id}", response_model=ApiResponse[List[KbMemberResponse]])
async def list(kb_id: int, db: AsyncSession = Depends(get_async_db)):
  list_info = await get_kb_members_by_id_service(db, kb_id)
  return ApiResponse(data=list_info)

@kb_member_router.post("/add", response_model=ApiResponse[str])
async def add(req: KbMemberRequest, db: AsyncSession = Depends(get_async_db), current_user:User = Depends(get_current_user)):
  add_info = await add_kb_member_service(db, req.model_dump())
  return ApiResponse(data=add_info)

@kb_member_router.delete("/delete/{kb_member_id}", response_model=ApiResponse[str])
async def delete(kb_member_id: int, db: AsyncSession = Depends(get_async_db)):
  del_info = await del_kb_member_service(db, kb_member_id)
  return ApiResponse(data=del_info)

@kb_member_router.put("/update/{kb_member_id}", response_model=ApiResponse[str])
async def update(kb_member_id: int, req: KbMemberUpdateRequest, db: AsyncSession = Depends(get_async_db)):
  update_info = await update_kb_member_service(db, kb_member_id, req.model_dump(exclude_none=True))
  return ApiResponse(data=update_info)


router.include_router(kb_member_router)