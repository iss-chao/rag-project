# rag_vue

基于 Vue 3 + TypeScript + Vite 的 AI 知识库助手前端，通过 REST API、SSE 和 WebSocket 与 `rag_server` 通信。

## 功能

- 用户注册、登录和个人资料
- 知识库与文档管理、成员和角色管理
- 会话列表、历史消息及流式 RAG 对话
- ETL 任务状态查看和实时状态更新
- Markdown 渲染、代码高亮与内容净化

## 本地开发

在 `rag_vue` 目录执行：

```bash
npm ci
npm run dev
```

Vite 默认运行于 <http://localhost:5500>。生产构建：

```bash
npm run build
```

## 配置与部署

开发和生产环境分别使用 `.env.development`、`.env.production` 中的 `VITE_API_BASE_URL`；当前默认值为 `/api`，预期由代理转发至后端。默认后端地址为 `http://localhost:5000`，代理规则见 `vite.config.ts`；容器部署入口和 Nginx 配置位于仓库根目录。

需要同时运行 `rag_server` 并配置其数据库、Redis、RabbitMQ、模型服务、OSS 和向量库。若调整 API 前缀或代理目标，请确保前端代理、Nginx 和后端路由前缀一致。
