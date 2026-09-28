from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Enum
from models.base import Base

class ChatMessage(Base):
  __tablename__ = "chat_message"
  id = Column(Integer, primary_key=True, index=True)
  thread_id = Column(Integer, ForeignKey("chat_thread.id"), nullable=False, comment="会话ID")
  role = Column(Enum("user", "assistant"), nullable=False, comment="角色")
  content = Column(Text, nullable=False, comment="回答内容")
  reasoning_content = Column(Text, nullable=True, comment="模型思考过程")
  is_valid = Column(Integer, nullable=True, default=1, comment="1有效 0失效")
  like = Column(Integer, nullable=False, default=0, comment="点赞标记")
  create_time = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


  chat_thread = relationship("ChatThread", back_populates="chat_messages")