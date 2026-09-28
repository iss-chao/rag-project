from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime

class AuditLogRequest(BaseModel):
  user_id: int
  resource_type: str
  detail: str
  address: str | None

class AuditLogResponse(BaseModel):
  id: int
  detail: str
  address: str | None
  create_time: datetime
  username: str

  @model_validator(mode="before")
  def get_username_from_user_obj(cls, v):
      # values里面拿到auditlog的user对象，取username
      return {
         "id": v.id,
         "detail": v.detail,
         "address": v.address,
         "create_time": v.create_time,
         "username": v.user.username
      }
  class Config:
    from_attributes = True