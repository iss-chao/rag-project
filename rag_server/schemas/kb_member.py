from pydantic import BaseModel
from schemas.kb_role import KbRoleResponse
from schemas.auth import UserResponse

class KbMemberRequest(BaseModel):
  kb_id: int
  user_id: int
  role_id: int


class KbMemberUpdateRequest(BaseModel):
  role_id: int

class KbMemberResponse(KbMemberRequest):
  id: int
  user: UserResponse
  kb_role: KbRoleResponse

  class Config:
    from_attributes = True