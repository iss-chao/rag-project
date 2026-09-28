from redis.asyncio import client, ConnectionPool
import json
from core.config import settings

redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=10
)

redis_client = client.Redis(connection_pool=redis_pool)

async def save_message(session_id: str, role: str, content: str):
    # 从 列表右侧（尾部）插入数据
    msg = {"role": role, "content": content}
    await redis_client.rpush(f"chat:{session_id}", json.dumps(msg))
    await redis_client.ltrim(f"chat:{session_id}", 0, 19)  # 保留最近20条

async def get_history(session_id: str):
    # 获取列表一段范围内的数据
    # - `start`：起始下标，从 0 开始
    # - `end`：结束下标
    # - `-1` = 取 全部
    # - `0,19` = 取前 20 条
    return await redis_client.lrange(f"chat:{session_id}", 0, -1)

async def clear_history(session_id: str):
    # 删除整个 Key
    await redis_client.delete(f"chat:{session_id}")


