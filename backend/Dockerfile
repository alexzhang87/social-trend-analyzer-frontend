# 使用 Python 3.11 官方镜像 (标准版，包含更多构建工具)
FROM python:3.11

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
# The build context is the root of the repo, so we need to specify the path
COPY backend/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
# Copy only the backend application code into the container's WORKDIR
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]