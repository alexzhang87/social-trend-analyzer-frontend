#!/usr/bin/env python3
"""
Railway 数据库初始化脚本
在Railway部署后运行此脚本来初始化数据库
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        logger.info(f"数据库URL: {settings.DATABASE_URL}")
        
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

async def check_database_connection():
    """检查数据库连接"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            logger.info("数据库连接正常")
            return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False

async def main():
    """主函数"""
    logger.info("Railway 数据库初始化开始...")
    
    # 检查环境变量
    if not settings.DATABASE_URL:
        logger.error("DATABASE_URL 环境变量未设置")
        sys.exit(1)
    
    # 检查数据库连接
    if not await check_database_connection():
        logger.error("无法连接到数据库")
        sys.exit(1)
    
    # 初始化数据库
    await init_database()
    
    logger.info("Railway 数据库初始化完成！")

if __name__ == "__main__":
    asyncio.run(main())