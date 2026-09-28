from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 获取环境
ENV = os.getenv("ENV", "dev")
print(f"当前环境: {ENV}")

# 加载环境变量
load_dotenv(".env")  # 加载默认的 .env 文件
load_dotenv(f".env.{ENV}")

class Settings(BaseSettings):
    SERVER_HOST: str
    SERVER_PORT: int
    
    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    # 数据库配置
    DATABASE_URL: str

    # oss
    ALIYUN_ACCESS_KEY_ID: str
    ALIYUN_ACCESS_KEY_SECRET: str
    OSS_ENDPOINT: str
    OSS_BUCKET: str

      # JWT配置
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # 模型配置
    API_KEY: str
    BASE_URL: str
    LLM_MODEL: str
    EMBEDDING_MODEL: str


    MAIN_SERVER_URL: str

    MILVUS_URI: str
    VECTOR_STORE_NAME: str

    RABBITMQ_URL: str

    CHROMA_PERSIST_PATH: str
    CHROMA_SERVER_HOST: str
    CHROMA_SERVER_PORT: int
    


settings = Settings()
