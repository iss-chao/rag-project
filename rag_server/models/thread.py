from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from models.base import Base

class ChatThread(Base):
  __tablename__ = "chat_thread"
  id=Column(Integer, primary_key=True, index=True)
  user_id=Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
  title=Column(String(255), nullable=False, comment="会话标题")
  kb_ids=Column(String(255), nullable=False, comment="知识库ID列表")
  create_time=Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
  update_time=Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")