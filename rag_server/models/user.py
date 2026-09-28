# 数据库模型
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class User(Base):
    __tablename__ = "users"  # 表名

    id = Column(Integer, primary_key=True, index=True)  # 主键
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")  # 用户名
    hashed_password = Column(String(255), nullable=False, comment="哈希密码")  # 哈希密码
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")  # 创建时间


    # 被依赖
    chat_thread = relationship("ChatThread", back_populates="user")
    documents = relationship("Document", back_populates="user")
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")
    etl_tasks = relationship("ETLTask", back_populates="user")
    user_role = relationship("UserRole", back_populates="user")
    kb_members = relationship("KbMember", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    rag_dataset = relationship("RAGDataset", back_populates="user")