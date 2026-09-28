from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class KbRole(Base):
  __tablename__ = "kb_roles"

  id = Column(Integer, primary_key=True, index=True)
  role_name = Column(String(20), nullable=False, comment="角色名称")
  role_code = Column(String(20), nullable=False, comment="角色代码")

  kb_members = relationship("KbMember", back_populates="kb_role")