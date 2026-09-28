from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class RAGDataset(Base):
  __tablename__ = "rag_dataset"
  id = Column(Integer, primary_key=True, index=True)
  kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
  owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID")
  question = Column(String(255), nullable=False, comment="问题")
  expected_segment_ids = Column(String(255), nullable=False, comment="预期分片ID列表")
  expected_answers = Column(String(255), nullable=False, comment="预期回答")

  knowledge_base = relationship("KnowledgeBase", back_populates="rag_dataset")
  user = relationship("User", back_populates="rag_dataset")