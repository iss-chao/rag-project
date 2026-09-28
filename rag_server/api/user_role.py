from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.response import ApiResponse, PageQuery, ListDataResponse
from database_async import get_async_db
from schemas.user_role import UserRoleRequest, UserListResponse, UpdateUserRoleRequest
from core.security import get_current_user
from core.permission import require_user_role
from service.user_role import create_user_role_service, get_user_role_list_service, update_user_role_service, delete_user_role_service

router = APIRouter(
  tags=["用户角色"],
  prefix="/api/user_role",
  dependencies=[Depends(get_current_user)]
)

user_role_router = APIRouter(
  dependencies=[Depends(require_user_role)]
)

@user_role_router.post("/add", response_model=ApiResponse[str])
async def create_user_role(req: UserRoleRequest, db: AsyncSession = Depends(get_async_db)):
  res_info = await create_user_role_service(db, req.model_dump())
  return ApiResponse(data=res_info)


@user_role_router.get("/list", response_model=ApiResponse[ListDataResponse[UserListResponse]])
async def get_user_role_list(
  page_query:PageQuery = Depends(PageQuery),
  db: AsyncSession = Depends(get_async_db)
):
  res_info = await get_user_role_list_service(db, page_query)
  return ApiResponse(data=res_info)


@user_role_router.put("/update/{user_role_id}", response_model=ApiResponse[str])
async def update_user_role(user_role_id: int, req: UpdateUserRoleRequest, db: AsyncSession = Depends(get_async_db)):
  res_info = await update_user_role_service(db, user_role_id, req.model_dump())
  return ApiResponse(data=res_info)


@user_role_router.delete("/delete/{user_role_id}", response_model=ApiResponse[str])
async def delete_user_role(user_role_id: int, db: AsyncSession = Depends(get_async_db)):
  res_info = await delete_user_role_service(db, user_role_id)
  return ApiResponse(data=res_info)

router.include_router(user_role_router)