from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class UserRole(Base):
  __tablename__ = "user_role"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
  role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")


  user = relationship("User", back_populates="user_role")
  role = relationship("Role", back_populates="user_role")