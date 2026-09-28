from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class Role(Base):
  __tablename__ = "roles"

  id = Column(Integer, primary_key=True, index=True)
  role_name = Column(String(20), nullable=False, comment="角色名称")
  role_code = Column(String(20), nullable=False, comment="角色代码")

  user_role = relationship("UserRole", back_populates="role")