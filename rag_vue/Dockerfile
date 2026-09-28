# 阶段1：构建静态文件（node 环境）
FROM node:20-alpine AS builder
WORKDIR /app
# 先复制依赖文件，利用缓存加速构建
COPY package*.json ./
RUN npm install
# 复制所有代码，执行构建
COPY . .
RUN npm run build

# 阶段2：用 Nginx 托管静态文件（体积小、性能好）
FROM nginx:alpine
# 把构建好的静态文件复制到 Nginx 默认目录
COPY --from=builder /app/dist /usr/share/nginx/html
# 暴露 80 端口
EXPOSE 80