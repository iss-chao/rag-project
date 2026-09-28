# 数据库模型
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base
from sqlalchemy.orm import relationship

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"  # 表名

    id = Column(Integer, primary_key=True, index=True)  # 主键
    name = Column(String(50), nullable=False, comment="知识库名称")
    description = Column(String(255), nullable=False, comment="知识库描述")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者者ID")
    visibility = Column(String(10), nullable=False, comment="知识库可见性")
    embedding_model = Column(String(50), nullable=False, comment="嵌入模型名称")
    rerank_model = Column(String(50), nullable=False, comment="rerank模型名称")
    is_valid = Column(Integer, nullable=True, default=1, comment="是否有效知识库")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 依赖
    user = relationship("User", back_populates="knowledge_bases")


    # 被依赖
    documents = relationship("Document", back_populates="knowledge_base")
    etl_tasks = relationship("ETLTask", back_populates="knowledge_base")
    kb_members = relationship("KbMember", back_populates="knowledge_base")
    rag_dataset = relationship("RAGDataset", back_populates="knowledge_base")
    