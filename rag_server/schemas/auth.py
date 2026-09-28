from pydantic import BaseModel, Field, field_validator, model_validator


# 用户请求模型
class UserReqest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

    @field_validator("username")
    def check_username_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("username不能为空")
        if len(v.strip()) < 3:
            raise ValueError("username长度必须至少3个字符")
        return v.strip()

    @field_validator("password")
    def check_password_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("password不能为空")
        if len(v.strip()) < 6:
            raise ValueError("password长度必须至少6个字符")
        return v.strip()

class RoleUserResponse(BaseModel):
  id: int | None
  user_id: int | None
#   user_name: str
  role_name: str | None
  role_code: str | None

  @model_validator(mode="before")
  def get_role(cls, v):
    return {
      "id": v.id if v else None,
      "user_id": v.user.id if v and v.user else None,
    #   "user_name": v.user.username,
      "role_name": v.role.role_name if v and v.role else None,
      "role_code": v.role.role_code if v and v.role else None
    }

  class Config:
    from_attributes = True


# 登录响应模型（返回Token和用户信息）
class LoginResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    refresh_token: str = Field(..., description="刷新令牌")
    # userinfo: dict = Field(..., description="用户信息", example={"username": "testuser", "user_id": 1})
    # user_role: RoleUserResponse


class RegisterResponse(BaseModel):
    content: str = Field(..., description="注册结果")
    username: str = Field(..., description="注册的用户名")


class UserResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    user_role: RoleUserResponse

    class Config:
        from_attributes = True



