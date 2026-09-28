from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship



class Segment(Base):
  __tablename__ = "segment"

  id = Column(Integer, primary_key=True, index=True)
  doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False, comment="文档ID")
  kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
  content = Column(Text, nullable=False, comment="分片文本内容")
  vector_id = Column(String(255), nullable=True, comment="PG向量唯一标识")
  meta_data = Column(Text, nullable=False, comment="分片文本元信息")
  page_no = Column(Integer, nullable=False, comment="页码")
  chunk_index = Column(Integer, nullable=False, comment="分片序号")
  is_valid = Column(Integer, nullable=True, default=1, comment="是否有效分片")
  create_time = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
