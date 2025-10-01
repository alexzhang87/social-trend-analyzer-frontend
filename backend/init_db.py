#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.data.models.database import create_db_and_tables, SessionLocal, User, UserRole, SubscriptionTier
from app.core.auth import get_password_hash
from app.core.config import settings
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 创建数据库表
        create_db_and_tables()
        logger.info("数据库表创建成功")
        
        # 创建默认管理员用户
        db = SessionLocal()
        try:
            # 检查是否已存在管理员用户
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin_user:
                # 创建默认管理员用户
                default_admin = User(
                    email=settings.ADMIN_EMAIL,
                    username="admin",
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                    full_name="系统管理员",
                    is_active=True,
                    is_verified=True,
                    role=UserRole.ADMIN,
                    subscription_tier=SubscriptionTier.PRO,
                    credits_balance=1000  # 管理员账户1000积分
                )
                db.add(default_admin)
                db.commit()
                logger.info(f"默认管理员用户创建成功: {settings.ADMIN_EMAIL}")
            else:
                logger.info("管理员用户已存在")
                
            # 创建测试用户
            test_user = db.query(User).filter(User.email == "test@example.com").first()
            if not test_user:
                test_user = User(
                    email="test@example.com",
                    username="testuser",
                    hashed_password=get_password_hash("test123"),
                    full_name="测试用户",
                    is_active=True,
                    is_verified=True,
                    role=UserRole.USER,
                    subscription_tier=SubscriptionTier.FREE,
                    credits_balance=10
                )
                db.add(test_user)
                db.commit()
                logger.info("测试用户创建成功: test@example.com")
            else:
                logger.info("测试用户已存在")
                
        except Exception as e:
            logger.error(f"创建用户时出错: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def reset_database():
    """重置数据库（删除所有数据）"""
    try:
        logger.warning("开始重置数据库...")
        
        # 删除数据库文件（仅适用于SQLite）
        if settings.DATABASE_URL.startswith("sqlite"):
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                os.remove(db_path)
                logger.info(f"数据库文件已删除: {db_path}")
        
        # 重新初始化
        init_database()
        
    except Exception as e:
        logger.error(f"数据库重置失败: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument("--reset", action="store_true", help="重置数据库")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()