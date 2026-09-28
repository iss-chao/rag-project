from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional, Annotated
from pydantic import BeforeValidator

def str_to_int(v):
    if isinstance(v, str):
        return int(v)
    return v

class SegmentCreate(BaseModel):
  doc_id: int
  kb_id: int
  content: str
  meta_data: str
  page_no: int
  chunk_index: int



class SegmentResponse(BaseModel):
  id: int
  doc_id: int
  kb_id: int | None
  content: str
  vector_id: Optional[str]
  meta_data: str
  page_no: int
  chunk_index: int
  is_valid: Annotated[Optional[Literal[0,1]], BeforeValidator(str_to_int)]
  create_time: datetime

  class Config:
    from_attributes = True