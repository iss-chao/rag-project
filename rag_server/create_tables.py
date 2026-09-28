import asyncio
from sqlalchemy import text
from database_async import async_engine, create_database_if_not_exists
from models.base import Base
from models import *


async def main():
    await create_database_if_not_exists()

    async with async_engine.begin() as conn:
        # await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️  所有旧表删除完毕")

        print(Base.metadata.tables)

        # await conn.run_sync(Base.metadata.create_all)
        # print("🎉 全部数据表创建成功！")

        # await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
