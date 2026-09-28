from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class AuditLog(Base):
  __tablename__ = "audit_log"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
  resource_type = Column(String(128), nullable=False, comment="操作类型")
  detail = Column(String(128), nullable=False, comment="操作详情")
  address = Column(String(128), nullable=True, comment="操作地址")
  create_time = Column(DateTime, nullable=False, default=func.now())

  user = relationship("User", back_populates="audit_logs")