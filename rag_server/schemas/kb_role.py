from pydantic import BaseModel

class KbRoleResponse(BaseModel):
  id: int
  role_name: str
  role_code: str

  class Config:
    from_attributes = True