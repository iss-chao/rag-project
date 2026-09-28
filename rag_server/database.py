# 数据库连接配置
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engine(settings.DATABASE_URL)  # 创建数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 创建数据库会话

def get_db():
    db = SessionLocal()  # 创建数据库会话
    try:
        yield db  # 生成器，提供数据库会话
    finally:
        db.close()  # 关闭数据库会话