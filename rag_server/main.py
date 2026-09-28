from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import os
from utils.error import http_exception_handler, validation_exception_handler, integrity_error_handler
from core.logger import logger
from core.config import settings
from utils.redis_task import redis_task_subscriber
from utils.mq import rabbitmq_client
from api.auth import router as auth_router
from api.document import router as document_router
from api.knowledge_base import router as knowledge_base_router
from api.user_role import router as user_role_router
from api.kb_member import router as kb_member_router
from api.etl_task import router as etl_task_router
from api.audit_log import router as audit_log_router
from api.chat_thread import router as thread_router
from api.chat_message import router as chat_router
from api.role import router as role_router
from api.kb_role import router as kb_role_router
from api.ws import router as ws_router, kb_connections

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info("服务启动成功")

    redis_sub_task = asyncio.create_task(redis_task_subscriber(kb_connections))
    logger.info(f"✅ redis订阅后台任务已创建，task:{redis_sub_task.get_name()}")

    # 连接mq
    await rabbitmq_client.connect()
    await rabbitmq_client.declare_queue("async_tasks")
    
    # 关闭时
    yield
    logger.info("服务关闭")
    try:
      redis_sub_task.cancel()
    except Exception as e:
      logger.error(f"❌ redis订阅后台任务取消失败: {e}", exc_info=True)

app = FastAPI(title="AI智能助手", version="1.0", lifespan=lifespan)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 全局异常
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)


# 路由
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(knowledge_base_router)
app.include_router(chat_router)
app.include_router(user_role_router)
app.include_router(kb_member_router)
app.include_router(etl_task_router)
app.include_router(audit_log_router)
app.include_router(thread_router)
app.include_router(role_router)
app.include_router(kb_role_router)
app.include_router(ws_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)