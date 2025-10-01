#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试账号创建脚本
用于创建不同套餐的测试用户账号
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.models.database import User, SubscriptionTier, UserRole, get_db
from app.core.auth import get_password_hash
from app.data.models.database import engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts():
    """
    创建测试账号
    """
    db = SessionLocal()
    
    try:
        # 测试账号数据
        test_accounts = [
            {
                "email": "free@test.com",
                "username": "free_user",
                "password": "test123456",
                "full_name": "Free User",
                "subscription_tier": SubscriptionTier.FREE,
                "credits_balance": 10,
                "is_verified": True,
                "subscription_expires_at": None
            },
            {
                "email": "pro@test.com",
                "username": "pro_user",
                "password": "test123456",
                "full_name": "Pro User",
                "subscription_tier": SubscriptionTier.PRO,
                "credits_balance": 1000,
                "is_verified": True,
                "subscription_expires_at": datetime.utcnow() + timedelta(days=30)
            },
            {
                "email": "plus@test.com",
                "username": "plus_user",
                "password": "test123456",
                "full_name": "Plus User",
                "subscription_tier": SubscriptionTier.PLUS,
                "credits_balance": 5000,
                "is_verified": True,
                "subscription_expires_at": datetime.utcnow() + timedelta(days=30)
            },
            {
                "email": "enterprise@test.com",
                "username": "enterprise_user",
                "password": "test123456",
                "full_name": "Enterprise User",
                "subscription_tier": SubscriptionTier.ENTERPRISE,
                "credits_balance": 10000,
                "is_verified": True,
                "subscription_expires_at": datetime.utcnow() + timedelta(days=365)
            },
            {
                "email": "admin@test.com",
                "username": "admin_user",
                "password": "admin123456",
                "full_name": "Admin User",
                "subscription_tier": SubscriptionTier.ENTERPRISE,
                "credits_balance": 99999,
                "is_verified": True,
                "role": UserRole.ADMIN,
                "subscription_expires_at": datetime.utcnow() + timedelta(days=365)
            }
        ]
        
        created_accounts = []
        
        for account_data in test_accounts:
            # 检查用户是否已存在
            existing_user = db.query(User).filter(
                (User.email == account_data["email"]) | 
                (User.username == account_data["username"])
            ).first()
            
            if existing_user:
                print(f"用户 {account_data['email']} 已存在，跳过创建")
                continue
            
            # 创建新用户
            user_data = account_data.copy()
            password = user_data.pop("password")
            user_data["hashed_password"] = get_password_hash(password)
            
            if "role" not in user_data:
                user_data["role"] = UserRole.USER
            
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            created_accounts.append({
                "email": account_data["email"],
                "password": password,
                "subscription_tier": account_data["subscription_tier"].value,
                "credits_balance": account_data["credits_balance"]
            })
            
            print(f"✅ 创建用户: {account_data['email']} ({account_data['subscription_tier'].value})")
        
        print("\n" + "="*60)
        print("测试账号创建完成！")
        print("="*60)
        
        for account in created_accounts:
            print(f"邮箱: {account['email']}")
            print(f"密码: {account['password']}")
            print(f"套餐: {account['subscription_tier'].upper()}")
            print(f"积分: {account['credits_balance']}")
            print("-" * 40)
        
        return created_accounts
        
    except Exception as e:
        print(f"创建测试账号时出错: {e}")
        db.rollback()
        return []
    finally:
        db.close()

if __name__ == "__main__":
    print("开始创建测试账号...")
    accounts = create_test_accounts()
    
    if accounts:
        print(f"\n成功创建 {len(accounts)} 个测试账号")
        print("\n📧 邮箱验证逻辑说明:")
        print("1. 注册时需要邮箱验证码验证")
        print("2. 验证码6位数字，有效期10分钟")
        print("3. 验证码存储在Redis中，自动过期")
        print("4. 忘记密码功能发送重置链接，有效期30分钟")
        print("5. 邮件使用HTML模板，包含品牌样式")
        
        print("\n💰 邮件服务费用说明:")
        print("- Gmail免费版: 每天500封邮件")
        print("- Gmail付费版: 无限制")
        print("- SendGrid免费版: 每月100封邮件")
        print("- SendGrid付费版: $14.95/月起")
        print("- 阿里云邮件推送: ¥1/千封起")
    else:
        print("未创建任何新账号")