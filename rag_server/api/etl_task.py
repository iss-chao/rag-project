from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from service.etl_task import get_etl_task_service, get_etl_task_list_service
from models.user import User
from core.security import get_current_user
from database_async import get_async_db
from typing import List
from schemas.etl_task import ETLTaskResponse
from schemas.response import ApiResponse

router = APIRouter(
  tags=["异步任务"],
  prefix="/api/etl_task"
)


@router.get("/detail/{task_id}", response_model=ApiResponse[ETLTaskResponse])
async def get_etl_task(task_id, db: AsyncSession = Depends(get_async_db)):
  task_info = await get_etl_task_service(db, task_id)
  return ApiResponse(data=task_info)

@router.get("/list", response_model=ApiResponse[List[ETLTaskResponse]])
async def get_etl_task_list(kb_id: int | None = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
  task_list = await get_etl_task_list_service(db, current_user.id, kb_id)
  return ApiResponse(data=task_list)