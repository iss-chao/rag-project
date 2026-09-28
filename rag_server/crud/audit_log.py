from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.audit_log import AuditLog
from sqlalchemy import select
from schemas.audit_log import AuditLogResponse

async def add_audit_log(db: AsyncSession, payload: dict):
  audit_log = AuditLog(**payload)
  db.add(audit_log)
  await db.flush()
  return audit_log

async def get_audit_log_list(db: AsyncSession):
  stmt = select(AuditLog).options(selectinload(AuditLog.user))
  logs = (await db.scalars(stmt)).all()
  return [AuditLogResponse.model_validate(log) for log in logs]