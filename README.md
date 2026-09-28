# RAG 知识库助手

一个由 Vue 前端和 FastAPI 后端组成的知识库问答项目，支持文档入库、向量检索和流式 AI 对话。

## 项目组成

- [rag_vue](rag_vue/README.md)：用户界面，提供认证、知识库与文档管理、会话聊天、任务及用户管理。
- [rag_server](rag_server/README.md)：API 与后台任务服务，负责认证、文档处理、RAG 检索、模型调用和权限管理。

## 运行方式

本地开发时分别按两个子项目的 README 安装依赖并启动。容器部署可从仓库根目录执行：

```bash
docker compose up -d --build
```

当前 Compose 提供 RabbitMQ、Chroma、Milvus 及 API、Worker、前端服务；MySQL、Redis、OSS 和 LLM/Embedding 服务需自行准备，并配置 `rag_server` 环境变量。前端默认端口为 `5500`，后端 API 为 `5000`。

首次部署前请检查环境变量、数据库迁移和根目录 `nginx.conf` 中的 API 转发规则。不要将真实密钥提交到仓库。
