#!/usr/bin/env python3
"""
云端部署配置和管理
支持AWS、Azure、Google Cloud等平台
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CloudDeploymentManager:
    """云端部署管理器"""
    
    def __init__(self):
        self.deployment_config = {
            'aws': {
                'service': 'EC2',
                'instance_type': 't3.medium',
                'region': 'us-east-1',
                'storage': '50GB',
                'auto_scaling': True,
                'estimated_cost': '$30-50/month'
            },
            'azure': {
                'service': 'Virtual Machines',
                'vm_size': 'Standard_B2s',
                'region': 'East US',
                'storage': '50GB',
                'auto_scaling': True,
                'estimated_cost': '$25-45/month'
            },
            'gcp': {
                'service': 'Compute Engine',
                'machine_type': 'e2-medium',
                'region': 'us-central1',
                'storage': '50GB',
                'auto_scaling': True,
                'estimated_cost': '$20-40/month'
            },
            'heroku': {
                'service': 'Dyno',
                'dyno_type': 'Standard-1X',
                'region': 'US',
                'storage': 'PostgreSQL Hobby',
                'auto_scaling': False,
                'estimated_cost': '$25/month'
            }
        }
        
        logger.info("云端部署管理器初始化完成")

    def generate_dockerfile(self) -> str:
        """生成Docker配置文件"""
        dockerfile_content = """
# 使用Python 3.9官方镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 设置权限
RUN chmod +x /app/enterprise_data_collector.py

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "enterprise_data_collector.py"]
"""
        return dockerfile_content.strip()

    def generate_requirements_txt(self) -> str:
        """生成Python依赖文件"""
        requirements = """
aiohttp==3.8.5
asyncio==3.4.3
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
sqlalchemy==2.0.19
psycopg2-binary==2.9.7
redis==4.6.0
celery==5.3.1
schedule==1.2.0
python-dotenv==1.0.0
pydantic==2.1.1
fastapi==0.101.1
uvicorn==0.23.2
prometheus-client==0.17.1
sentry-sdk==1.29.2
"""
        return requirements.strip()

    def generate_docker_compose(self) -> str:
        """生成Docker Compose配置"""
        compose_content = """
version: '3.8'

services:
  data-collector:
    build: .
    container_name: ideaeden-collector
    restart: unless-stopped
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - GITHUB_TOKEN_1=${GITHUB_TOKEN_1}
      - GITHUB_TOKEN_2=${GITHUB_TOKEN_2}
      - GITHUB_TOKEN_3=${GITHUB_TOKEN_3}
      - TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - ideaeden-network

  postgres:
    image: postgres:15
    container_name: ideaeden-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=ideaeden
      - POSTGRES_USER=ideaeden
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - ideaeden-network

  redis:
    image: redis:7-alpine
    container_name: ideaeden-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - ideaeden-network

  nginx:
    image: nginx:alpine
    container_name: ideaeden-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - data-collector
    networks:
      - ideaeden-network

volumes:
  postgres_data:
  redis_data:

networks:
  ideaeden-network:
    driver: bridge
"""
        return compose_content.strip()

    def generate_aws_cloudformation(self) -> Dict:
        """生成AWS CloudFormation模板"""
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "IdeaEden Data Collector Infrastructure",
            "Parameters": {
                "InstanceType": {
                    "Type": "String",
                    "Default": "t3.medium",
                    "Description": "EC2 instance type"
                },
                "KeyName": {
                    "Type": "AWS::EC2::KeyPair::KeyName",
                    "Description": "EC2 Key Pair for SSH access"
                }
            },
            "Resources": {
                "VPC": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": "10.0.0.0/16",
                        "EnableDnsHostnames": True,
                        "EnableDnsSupport": True,
                        "Tags": [{"Key": "Name", "Value": "IdeaEden-VPC"}]
                    }
                },
                "PublicSubnet": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "VpcId": {"Ref": "VPC"},
                        "CidrBlock": "10.0.1.0/24",
                        "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                        "MapPublicIpOnLaunch": True,
                        "Tags": [{"Key": "Name", "Value": "IdeaEden-PublicSubnet"}]
                    }
                },
                "InternetGateway": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [{"Key": "Name", "Value": "IdeaEden-IGW"}]
                    }
                },
                "AttachGateway": {
                    "Type": "AWS::EC2::VPCGatewayAttachment",
                    "Properties": {
                        "VpcId": {"Ref": "VPC"},
                        "InternetGatewayId": {"Ref": "InternetGateway"}
                    }
                },
                "SecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": "Security group for IdeaEden collector",
                        "VpcId": {"Ref": "VPC"},
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 22,
                                "ToPort": 22,
                                "CidrIp": "0.0.0.0/0"
                            },
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 80,
                                "ToPort": 80,
                                "CidrIp": "0.0.0.0/0"
                            },
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 443,
                                "ToPort": 443,
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "Tags": [{"Key": "Name", "Value": "IdeaEden-SG"}]
                    }
                },
                "EC2Instance": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": "ami-0c02fb55956c7d316",  # Amazon Linux 2
                        "InstanceType": {"Ref": "InstanceType"},
                        "KeyName": {"Ref": "KeyName"},
                        "SecurityGroupIds": [{"Ref": "SecurityGroup"}],
                        "SubnetId": {"Ref": "PublicSubnet"},
                        "UserData": {
                            "Fn::Base64": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "#!/bin/bash\n",
                                        "yum update -y\n",
                                        "yum install -y docker\n",
                                        "service docker start\n",
                                        "usermod -a -G docker ec2-user\n",
                                        "curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose\n",
                                        "chmod +x /usr/local/bin/docker-compose\n",
                                        "mkdir -p /home/ec2-user/ideaeden\n",
                                        "cd /home/ec2-user/ideaeden\n",
                                        "# 这里可以添加代码下载和启动逻辑\n"
                                    ]
                                ]
                            }
                        },
                        "Tags": [{"Key": "Name", "Value": "IdeaEden-Collector"}]
                    }
                }
            },
            "Outputs": {
                "InstanceId": {
                    "Description": "Instance ID of the EC2 instance",
                    "Value": {"Ref": "EC2Instance"}
                },
                "PublicIP": {
                    "Description": "Public IP address of the EC2 instance",
                    "Value": {"Fn::GetAtt": ["EC2Instance", "PublicIp"]}
                }
            }
        }
        return template

    def generate_kubernetes_deployment(self) -> str:
        """生成Kubernetes部署配置"""
        k8s_config = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ideaeden-collector
  labels:
    app: ideaeden-collector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ideaeden-collector
  template:
    metadata:
      labels:
        app: ideaeden-collector
    spec:
      containers:
      - name: collector
        image: ideaeden/data-collector:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDDIT_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: reddit-client-id
        - name: REDDIT_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: reddit-client-secret
        - name: GITHUB_TOKEN_1
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: github-token-1
        - name: TWITTER_BEARER_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: twitter-bearer-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        volumeMounts:
        - name: data-storage
          mountPath: /app/data
        - name: logs-storage
          mountPath: /app/logs
      volumes:
      - name: data-storage
        persistentVolumeClaim:
          claimName: data-pvc
      - name: logs-storage
        persistentVolumeClaim:
          claimName: logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ideaeden-collector-service
spec:
  selector:
    app: ideaeden-collector
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
"""
        return k8s_config.strip()

    def generate_monitoring_config(self) -> str:
        """生成监控配置"""
        prometheus_config = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ideaeden-collector'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
"""
        return prometheus_config.strip()

    def generate_deployment_script(self, platform: str = 'aws') -> str:
        """生成部署脚本"""
        if platform == 'aws':
            script = """#!/bin/bash
set -e

echo "开始AWS部署..."

# 检查AWS CLI
if ! command -v aws &> /dev/null; then
    echo "请先安装AWS CLI"
    exit 1
fi

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "请先安装Docker"
    exit 1
fi

# 创建部署目录
mkdir -p ideaeden-deployment
cd ideaeden-deployment

# 下载配置文件
echo "下载配置文件..."
# 这里可以从Git仓库或其他地方下载

# 构建Docker镜像
echo "构建Docker镜像..."
docker build -t ideaeden/data-collector:latest .

# 推送到ECR（如果需要）
# aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
# docker tag ideaeden/data-collector:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ideaeden:latest
# docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ideaeden:latest

# 部署CloudFormation堆栈
echo "部署基础设施..."
aws cloudformation deploy \\
    --template-file cloudformation.yaml \\
    --stack-name ideaeden-infrastructure \\
    --parameter-overrides KeyName=your-key-pair \\
    --capabilities CAPABILITY_IAM

# 获取实例IP
INSTANCE_IP=$(aws cloudformation describe-stacks \\
    --stack-name ideaeden-infrastructure \\
    --query 'Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue' \\
    --output text)

echo "部署完成！"
echo "实例IP: $INSTANCE_IP"
echo "请等待几分钟让服务启动完成"
"""
        elif platform == 'heroku':
            script = """#!/bin/bash
set -e

echo "开始Heroku部署..."

# 检查Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "请先安装Heroku CLI"
    exit 1
fi

# 登录Heroku
heroku login

# 创建应用
heroku create ideaeden-collector-$(date +%s)

# 设置环境变量
heroku config:set REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID
heroku config:set REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET
heroku config:set GITHUB_TOKEN_1=$GITHUB_TOKEN_1
heroku config:set TWITTER_BEARER_TOKEN=$TWITTER_BEARER_TOKEN

# 添加数据库
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev

# 部署代码
git add .
git commit -m "Deploy to Heroku"
git push heroku main

echo "Heroku部署完成！"
heroku open
"""
        else:
            script = """#!/bin/bash
echo "请选择支持的平台: aws, heroku"
exit 1
"""
        
        return script.strip()

    def save_deployment_files(self, output_dir: str = "./deployment"):
        """保存所有部署文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存Docker文件
        with open(f"{output_dir}/Dockerfile", "w") as f:
            f.write(self.generate_dockerfile())
        
        with open(f"{output_dir}/requirements.txt", "w") as f:
            f.write(self.generate_requirements_txt())
        
        with open(f"{output_dir}/docker-compose.yml", "w") as f:
            f.write(self.generate_docker_compose())
        
        # 保存云平台配置
        with open(f"{output_dir}/cloudformation.yaml", "w") as f:
            json.dump(self.generate_aws_cloudformation(), f, indent=2)
        
        with open(f"{output_dir}/kubernetes.yaml", "w") as f:
            f.write(self.generate_kubernetes_deployment())
        
        # 保存监控配置
        with open(f"{output_dir}/prometheus.yml", "w") as f:
            f.write(self.generate_monitoring_config())
        
        # 保存部署脚本
        with open(f"{output_dir}/deploy-aws.sh", "w") as f:
            f.write(self.generate_deployment_script('aws'))
        
        with open(f"{output_dir}/deploy-heroku.sh", "w") as f:
            f.write(self.generate_deployment_script('heroku'))
        
        # 设置脚本执行权限
        os.chmod(f"{output_dir}/deploy-aws.sh", 0o755)
        os.chmod(f"{output_dir}/deploy-heroku.sh", 0o755)
        
        logger.info(f"部署文件已保存到: {output_dir}")

    def get_deployment_guide(self) -> str:
        """获取部署指南"""
        guide = """
# IdeaEden数据收集系统云端部署指南

## 1. 准备工作

### API密钥配置
请确保已获取以下API密钥：
- Reddit: CLIENT_ID, CLIENT_SECRET
- GitHub: Personal Access Tokens (建议5个)
- Twitter: Bearer Token (API v2)

### 环境变量设置
```bash
export REDDIT_CLIENT_ID="your_reddit_client_id"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret"
export GITHUB_TOKEN_1="your_github_token_1"
export GITHUB_TOKEN_2="your_github_token_2"
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
```

## 2. 部署选项

### 选项1: AWS部署 (推荐)
- 成本: $30-50/月
- 性能: 高
- 可扩展性: 优秀
- 部署命令: `./deploy-aws.sh`

### 选项2: Heroku部署 (简单)
- 成本: $25/月
- 性能: 中等
- 可扩展性: 有限
- 部署命令: `./deploy-heroku.sh`

### 选项3: 自建服务器
- 成本: 取决于服务器
- 性能: 可控
- 可扩展性: 可控
- 部署命令: `docker-compose up -d`

## 3. 监控和维护

### 数据收集监控
- 访问: http://your-server/dashboard
- 查看收集统计、错误日志、系统状态

### 日志查看
```bash
docker logs ideaeden-collector
```

### 数据备份
系统会自动备份数据到云存储，建议定期检查备份状态。

## 4. 故障排除

### 常见问题
1. API限制: 系统会自动处理，但可能影响收集速度
2. 存储空间: 监控磁盘使用，及时清理旧数据
3. 网络问题: 检查防火墙和安全组设置

### 联系支持
如遇问题，请查看日志文件或联系技术支持。
"""
        return guide.strip()

# 使用示例
if __name__ == "__main__":
    manager = CloudDeploymentManager()
    
    # 生成所有部署文件
    manager.save_deployment_files("./deployment")
    
    # 显示部署指南
    print(manager.get_deployment_guide())
    
    print("\n部署文件已生成完成！")
    print("请查看 ./deployment 目录中的文件")