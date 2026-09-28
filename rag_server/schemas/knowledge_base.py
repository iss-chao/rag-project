from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Literal, Optional

class KnowledgeBaseRequest(BaseModel):
  name: str
  description: str
  visibility: Literal["public", "private"]
  embedding_model: str
  rerank_model: str


class KnowledgeBaseUpdateRequest(BaseModel):
  name: Optional[str] = None
  description: Optional[str] = None
  visibility: Optional[Literal["public", "private"]] = None
  embedding_model: Optional[str] = None
  rerank_model: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
  id: int
  name: str
  description: str
  owner_id: int
  visibility: Literal["public", "private"]
  embedding_model: str
  rerank_model: str
  created_at: datetime
  owner_name: Optional[str]

  @model_validator(mode="before")
  def get_username_from_user_obj(cls, v):
    # values里面拿到auditlog的user对象，取username
    return {
       "id": v.id,
       "name": v.name,
       "description": v.description,
       "owner_id": v.owner_id,
       "visibility": v.visibility,
       "embedding_model": v.embedding_model,
       "rerank_model": v.rerank_model,
       "created_at": v.created_at,
       "owner_name": getattr(v.user, "username", None)
    }


  class Config:
    from_attributes = True