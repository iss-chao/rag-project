# 服务
SERVER_PORT=5000
SERVER_HOST=0.0.0.0

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis123456


# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@mysql:3306/rag_server?charset=utf8mb4


CHROMA_PERSIST_PATH=./chroma_db
CHROMA_SERVER_HOST=chroma
CHROMA_SERVER_PORT=8000



API_KEY=sk-f0716c23631b4054a9f2846a73a5594c
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3.7-flash-2026-07-15
EMBEDDING_MODEL=qwen3.7-text-embedding


MAIN_SERVER_URL=http://120.26.132.106
MILVUS_URI=http://milvus-standalone:19530

VECTOR_STORE_NAME=milvus

RABBITMQ_URL=amqp://guest:guest@rabbitmq/