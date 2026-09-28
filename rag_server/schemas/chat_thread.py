from pydantic import BaseModel

class ChatThreadCreate(BaseModel):
  title: str | None
  kb_ids: str


class ChatThreadResponse(BaseModel):
  id: int
  user_id: int
  title: str | None
  kb_ids: str

  class Config:
    from_attributes = True