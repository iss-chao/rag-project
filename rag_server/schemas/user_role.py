from pydantic import BaseModel, model_validator
from schemas.auth import UserResponse
from schemas.role import RoleResponse

class UserRoleRequest(BaseModel):
  user_id: int
  role_id: int


class UpdateUserRoleRequest(BaseModel):
  role_id: int

class DeleteUserRoleRequest(BaseModel):
  user_id: int


class UserListResponse(BaseModel):
  id: int
  user: UserResponse
  role: RoleResponse
  class Config:
    from_attributes = True

  