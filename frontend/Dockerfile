# 多阶段构建 Dockerfile for React + Vite 前端应用

# ========================================
# 开发阶段
# ========================================
FROM node:18-alpine as development

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production=false

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3001

# 开发模式启动命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]

# ========================================
# 构建阶段
# ========================================
FROM node:18-alpine as build

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# ========================================
# 生产阶段
# ========================================
FROM nginx:alpine as production

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]