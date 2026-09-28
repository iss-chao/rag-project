from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database_async import get_async_db
from schemas.response import ApiResponse
from core.security import get_current_user
from service.chat_thread import create_thread_service, thread_List_service, soft_del_thread_service, update_thread_title_service
from schemas.chat_thread import ChatThreadCreate, ChatThreadResponse
from models.user import User

router = APIRouter(
  tags=["会话管理"],
  prefix="/api/chat_thread",
  dependencies=[Depends(get_current_user)]
)

thread_router = APIRouter()

@router.post("/add", response_model=ApiResponse[ChatThreadResponse])
async def create_thread(req:ChatThreadCreate, db: AsyncSession = Depends(get_async_db), current_user:User = Depends(get_current_user)):
  payload = req.model_dump()
  payload["user_id"] = current_user.id
  new_thread = await create_thread_service(db, payload)
  return ApiResponse(data=new_thread)

@thread_router.get("/list", response_model=ApiResponse[List[ChatThreadResponse]])
async def get_thread_list(current_user:User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  list = await thread_List_service(db, current_user.id)
  return ApiResponse(data=list)


@thread_router.delete("/delete/{thread_id}", response_model=ApiResponse[str])
async def get_thread_list(thread_id:int, current_user:User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  del_info = await soft_del_thread_service(db, thread_id, current_user.id)
  return ApiResponse(data=del_info)

@thread_router.put("/rename/{thread_id}", response_model=ApiResponse[str])
async def rename_thread(thread_id:int, title:str, current_user:User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  rename_info = await update_thread_title_service(db, thread_id, title, current_user.id)
  return ApiResponse(data=rename_info)


router.include_router(thread_router)