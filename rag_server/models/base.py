from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

# Base = declarative_base()  # 创建基类，用于定义模型

class Base(DeclarativeBase):
  __abstract__ = True
  id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID")


class BaseAudit(Base):
  __abstract__ = True
  creator_id: Mapped[int] = mapped_column(comment="创建人ID")
  created_at: Mapped[DateTime] = mapped_column(
      DateTime(timezone=True),
      server_default=func.now(),
      comment="创建时间"
  )
  updated_at: Mapped[DateTime] = mapped_column(
      DateTime(timezone=True),
      onupdate=func.now(),
      comment="更新时间"
  )