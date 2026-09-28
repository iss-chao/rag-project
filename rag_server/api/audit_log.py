from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database_async import get_async_db
from service.audit_log import get_audit_log_list_service
from schemas.response import ApiResponse
from schemas.audit_log import AuditLogResponse

router = APIRouter(
  tags=["审计日志"],
  prefix="/api/audit_log"
)

audit_log_router = APIRouter(
  # dependencies=[Depends(get_audit_log_service)]
)

@audit_log_router.get("/list", response_model=ApiResponse[List[AuditLogResponse]])
async def list_audit_log(db: AsyncSession = Depends(get_async_db)):
  list_info = await get_audit_log_list_service(db)
  return ApiResponse(data=list_info)


router.include_router(audit_log_router)