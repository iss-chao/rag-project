import redis
from core.config import settings

redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    max_connections=10
)

redis_client = redis.Redis(connection_pool=redis_pool)

def save_message(session_id: str, role: str, content: str):
    # 从 列表左侧（头部）插入数据
    # rpush从右侧插入
    redis_client.lpush(f"chat:{session_id}", f"{role}:{content}")
    # 裁剪列表，只保留指定区间，删掉其余数据
    redis_client.ltrim(f"chat:{session_id}", 0, 19)  # 保留最近20条

def get_history(session_id: str):
    return redis_client.lrange(f"chat:{session_id}", 0, -1)

def clear_history(session_id: str):
    # 删除整个 Key
    redis_client.delete(f"chat:{session_id}")



