from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base

class KbMember(Base):
  __tablename__ = "kb_member"

  id = Column(Integer, primary_key=True, index=True)
  kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
  role_id = Column(Integer, ForeignKey("kb_roles.id"), nullable=False, comment="角色ID")
  created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


  knowledge_base = relationship("KnowledgeBase", back_populates="kb_members")
  user = relationship("User", back_populates="kb_members")
  kb_role = relationship("KbRole", back_populates="kb_members")