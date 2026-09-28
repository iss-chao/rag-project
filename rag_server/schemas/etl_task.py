from  pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from schemas.document import DocumentResponse
from schemas.knowledge_base import KnowledgeBaseResponse

class ETLTaskCreate(BaseModel):
  doc_id: int | None = None
  kb_id: int
  status: str
  task_type: str
  creator_id: int



class ETLTaskResponse(BaseModel):
  id: int
  doc_id: int | None = None
  kb_id: int | None = None
  task_type: str
  creator_id: int
  status: str | None
  retry_count: int | None
  fail_reason: str | None
  create_time: datetime | None
  finish_time: datetime | None
  document: DocumentResponse | None = Field(default=None, serialization_alias="doc")
  knowledge_base: KnowledgeBaseResponse | None = Field(default=None, serialization_alias="kb")

  
  class Config:
    from_attributes = True