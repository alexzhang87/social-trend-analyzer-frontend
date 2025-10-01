#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.models.database import SessionLocal, User, UserRole
from app.core.config import settings
from app.core.auth import get_password_hash

def check_and_create_admin():
    # 首先创建数据库表
    from app.data.models.database import create_db_and_tables
    create_db_and_tables()
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_user:
            print(f"管理员用户已存在: {admin_user.email}")
            print(f"用户名: {admin_user.username}")
            print(f"是否激活: {admin_user.is_active}")
            print(f"是否验证: {admin_user.is_verified}")
        else:
            print("未找到管理员用户，正在创建...")
            # 创建默认管理员用户
            from app.data.models.database import SubscriptionTier
            default_admin = User(
                email=settings.ADMIN_EMAIL,
                username="admin",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="系统管理员",
                is_active=True,
                is_verified=True,
                role=UserRole.ADMIN,
                subscription_tier=SubscriptionTier.PRO
            )
            db.add(default_admin)
            db.commit()
            print(f"默认管理员用户已创建: {settings.ADMIN_EMAIL}")
            
        # 给admin用户添加积分
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_user:
            # 设置积分余额为100积分用于测试
            admin_user.credits_balance = 100
            db.commit()
            print(f"\n已为管理员用户设置积分余额: {admin_user.credits_balance}")
            print(f"订阅等级: {admin_user.subscription_tier.value}")
            
        # 检查所有用户
        all_users = db.query(User).all()
        print(f"\n数据库中共有 {len(all_users)} 个用户:")
        for user in all_users:
            print(f"- {user.email} ({user.role.value}) - 激活: {user.is_active} - 积分: {user.credits_balance}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_admin()