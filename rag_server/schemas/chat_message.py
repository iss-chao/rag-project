from pydantic import BaseModel
from typing import Optional, Literal

class ChatMessageCreate(BaseModel):
  thread_id: int
  role: Literal["user", "assistant"]
  content: str
  reasoning_content: Optional[str] = None


class ChatMessageResponse(BaseModel):
  id: int
  thread_id: int
  role: Literal["user", "assistant"]
  content: str
  reasoning_content: Optional[str] = None
  like: int

  class Config:
    from_attributes = True