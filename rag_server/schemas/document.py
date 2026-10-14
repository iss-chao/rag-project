from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Literal, Optional, Annotated


class DocumentStatus(str, Enum):
  PENDING = "pending"
  PARSING = "parsing"
  SUCCESS = "success"
  FAILED = "failed"

# class DocumentStatus(str, Enum):
#   padding = "pending"
#   parsing = "parsing"
#   success = "success"
#   failed = "failed"

class DocumentCreate(BaseModel):
  kb_id: int
  name: str
  file_type: str
  file_size: int
  oss_key: str
  version: int
  status: Literal["pending", "parsing", "success", "failed"]
  creator_id: int


class DocumentUpdate(BaseModel):
  name: str | None = None
  file_type: str | None = None
  file_size: int | None = None
  oss_key: str | None = None
  version: int | None = None
  status: Literal["pending", "parsing", "success", "failed"]
  creator_id: int | None = None


class DocumentResponse(BaseModel):
  id: int
  kb_id: int
  name: str
  file_type: str
  file_size: int
  oss_key: str
  version: int
  is_valid: Literal[0,1]
  status: Literal["pending", "parsing", "success", "failed"]
  creator_id: int
  created_at: datetime
  update_time: datetime | None

  class Config:
    from_attributes = True