# 数据库模型
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from models.base import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"  # 表名

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True, comment="知识库ID")
    name = Column(String(255), nullable=False, comment="文档名称")
    file_type = Column(String(20), nullable=False, comment="文件类型")
    file_size = Column(Integer, nullable=False, comment="文件大小")
    oss_key = Column(String(255), nullable=False, comment="OSS文件路径")
    version = Column(Integer, nullable=False, comment="版本号")
    status = Column(String(20), nullable=False, comment="文档状态")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传人ID")
    is_valid = Column(Integer, nullable=True, default=1, comment="是否有效文档")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 依赖
    user = relationship("User", back_populates="documents")
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    # 反向依赖
    etl_tasks = relationship("ETLTask", back_populates="document")

    # from sqlalchemy.schema import UniqueConstraint
    # __table_args__ = (
    #   # 联合索引
    #   Index("idx_segment_kb_doc", "kb_id", "doc_id"),
    #   # 唯一索引
    #   UniqueConstraint("kb_id", "name", name="unique_document_name"),
    # )

    