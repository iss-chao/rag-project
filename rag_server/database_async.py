# database_async.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

# pip install aiomysql
# 拼接异步mysql链接，协议改为 mysql+aiomysql
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False
)

# 异步会话工厂
async_session_maker = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def get_async_db():
    db = async_session_maker()  # 创建数据库会话
    try:
        yield db  # 生成器，提供数据库会话
    finally:
        await db.close()  # 关闭数据库会话


async def create_database_if_not_exists():
    # 从异步连接地址拆分出数据库名
    db_name_with_params = ASYNC_DATABASE_URL.rsplit("/", 1)[-1]
    db_name = db_name_with_params.split("?")[0]
    url_without_db = ASYNC_DATABASE_URL.rsplit("/",1)[0]

    root_engine = create_async_engine(url_without_db)
    async with root_engine.begin() as conn:
        sql = text(f"""
            CREATE DATABASE IF NOT EXISTS {db_name}
            DEFAULT CHARACTER SET utf8mb4
            COLLATE utf8mb4_general_ci;
        """)
        await conn.execute(sql)
    await root_engine.dispose()
    print(f"✅ 数据库 {db_name} 校验/创建完成")