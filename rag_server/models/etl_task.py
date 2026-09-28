from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

class ETLTask(Base):
  __tablename__ = "etl_task"

  id = Column(Integer, primary_key=True, index=True)
  doc_id = Column(Integer,ForeignKey("documents.id"), nullable=True, comment="文档ID")
  creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID")
  kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
  task_type = Column(String(20), nullable=False, comment="任务类型")
  status = Column(String(20), nullable=True, comment="任务状态")
  retry_count = Column(Integer, nullable=True, comment="重试次数")
  fail_reason = Column(String(255), nullable=True, comment="失败原因")
  create_time = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
  finish_time = Column(DateTime(timezone=True), nullable=True, comment="完成时间")


  # 依赖
  document = relationship("Document", back_populates="etl_tasks")
  user = relationship("User", back_populates="etl_tasks")
  knowledge_base = relationship("KnowledgeBase", back_populates="etl_tasks")
