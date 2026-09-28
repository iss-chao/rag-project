# rag_server

AI 知识库问答系统的 FastAPI 后端，负责认证授权、知识库与文档管理、文档解析、RAG 检索问答及异步任务处理。

## 功能

- 用户注册、登录、Token 刷新、角色管理和知识库成员权限
- 知识库、文档、会话、聊天消息、任务及审计记录管理
- 文档上传至 OSS，并由后台任务解析、分片、生成向量
- 普通问答、SSE 流式问答和 WebSocket 任务状态推送
- Redis 保存对话历史；MySQL 保存业务数据；向量库可配置 Chroma 或 Milvus

## 技术栈

Python 3.12、FastAPI、SQLAlchemy、MySQL、Redis、RabbitMQ、Chroma/Milvus、LangChain，以及 OpenAI 兼容的大模型和 Embedding 服务。

## 本地运行

在 `rag_server` 目录执行：

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# 安装依赖
pip install -r requirements.txt
```

配置 `.env` 和 `.env.{ENV}`（默认 `ENV=dev`，即 `.env.dev`）。按 `core/config.py` 配置数据库、Redis、RabbitMQ、OSS、JWT、模型服务和向量库连接；请使用自己的密钥，不要提交凭据。数据库结构通过项目 `alembic/` 迁移管理，执行前确认数据库连接和迁移版本。

分别在两个终端启动 API 和队列 Worker：

```bash
python main.py
python worker_mq.py
```

API 文档：<http://localhost:5000/docs>。本地开发时从本目录启动，以确保环境变量和数据路径正确。

## 配套服务

运行需要 MySQL、Redis、RabbitMQ、可用的 LLM/Embedding 接口及 OSS。向量库由 `VECTOR_STORE_NAME` 选择；仓库根目录的 Compose 还提供 Chroma、Milvus 及其依赖服务。MySQL、Redis、OSS 和模型服务需按环境配置提供。

更多接口定义可通过运行中的 `/docs` 查看。
