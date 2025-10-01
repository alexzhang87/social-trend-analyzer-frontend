#!/usr/bin/env python3
"""
Stripe产品和价格设置脚本

这个脚本会自动在Stripe中创建所需的产品和价格。
运行前请确保：
1. 已在.env文件中配置了STRIPE_SECRET_KEY
2. 使用的是Stripe测试环境密钥（sk_test_开头）

使用方法：
python setup_stripe_products.py
"""

import os
import stripe
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

if not stripe.api_key:
    print("❌ 错误：未找到STRIPE_SECRET_KEY环境变量")
    print("请在.env文件中设置STRIPE_SECRET_KEY")
    exit(1)

if not stripe.api_key.startswith('sk_test_'):
    print("⚠️  警告：检测到生产环境密钥，请确认是否要在生产环境中创建产品")
    response = input("继续？(y/N): ")
    if response.lower() != 'y':
        exit(0)

def create_subscription_products():
    """创建订阅产品和价格"""
    print("🔄 创建订阅产品...")
    
    subscription_plans = [
        {
            'id': 'starter',
            'name': 'Starter Plan',
            'description': '适合个人用户的基础计划',
            'price': 999,  # $9.99
            'features': ['每月100次分析', '基础报告', '邮件支持']
        },
        {
            'id': 'pro',
            'name': 'Pro Plan',
            'description': '适合专业用户的高级计划',
            'price': 2999,  # $29.99
            'features': ['每月1000次分析', '高级报告', '优先支持', 'API访问']
        },
        {
            'id': 'plus',
            'name': 'Plus Plan',
            'description': '适合团队的增强计划',
            'price': 5999,  # $59.99
            'features': ['每月5000次分析', '团队协作', '自定义报告', '专属客服']
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise Plan',
            'description': '适合大型企业的定制计划',
            'price': 19999,  # $199.99
            'features': ['无限分析', '企业级安全', '定制集成', '专属支持']
        }
    ]
    
    created_prices = {}
    
    for plan in subscription_plans:
        try:
            # 创建产品
            product = stripe.Product.create(
                name=plan['name'],
                description=plan['description'],
                metadata={
                    'plan_id': plan['id'],
                    'features': ', '.join(plan['features'])
                }
            )
            
            # 创建价格
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan['price'],
                currency='usd',
                recurring={'interval': 'month'},
                metadata={
                    'plan_id': plan['id']
                }
            )
            
            created_prices[f"{plan['id']}_monthly"] = price.id
            print(f"✅ 创建订阅计划: {plan['name']} - {price.id}")
            
        except Exception as e:
            print(f"❌ 创建订阅计划 {plan['name']} 失败: {str(e)}")
    
    return created_prices

def create_credit_products():
    """创建积分包产品和价格"""
    print("🔄 创建积分包产品...")
    
    credit_packages = [
        {
            'id': 'small',
            'name': '小积分包',
            'description': '100积分 - 适合轻度使用',
            'price': 999,  # $9.99
            'credits': 100
        },
        {
            'id': 'medium',
            'name': '中积分包',
            'description': '500积分 - 适合中度使用',
            'price': 3999,  # $39.99
            'credits': 500
        },
        {
            'id': 'large',
            'name': '大积分包',
            'description': '1000积分 - 适合重度使用',
            'price': 6999,  # $69.99
            'credits': 1000
        }
    ]
    
    created_prices = {}
    
    for package in credit_packages:
        try:
            # 创建产品
            product = stripe.Product.create(
                name=package['name'],
                description=package['description'],
                metadata={
                    'package_id': package['id'],
                    'credits': str(package['credits'])
                }
            )
            
            # 创建价格
            price = stripe.Price.create(
                product=product.id,
                unit_amount=package['price'],
                currency='usd',
                metadata={
                    'package_id': package['id'],
                    'credits': str(package['credits'])
                }
            )
            
            created_prices[f"credits_{package['id']}"] = price.id
            print(f"✅ 创建积分包: {package['name']} - {price.id}")
            
        except Exception as e:
            print(f"❌ 创建积分包 {package['name']} 失败: {str(e)}")
    
    return created_prices

def update_price_mapping(all_prices):
    """更新价格映射文件"""
    print("🔄 更新价格映射...")
    
    mapping_content = f'''# Stripe价格ID映射
# 这个文件由setup_stripe_products.py自动生成
# 请将这些价格ID复制到payments.py中的STRIPE_PRICE_IDS字典

STRIPE_PRICE_IDS = {{
    # 订阅计划价格ID（月付）
'''
    
    for key, price_id in all_prices.items():
        if 'monthly' in key:
            plan_name = key.replace('_monthly', '').title()
            mapping_content += f'    "{key}": "{price_id}",  # {plan_name}计划\n'
    
    mapping_content += '\n    # 积分包价格ID（一次性购买）\n'
    
    for key, price_id in all_prices.items():
        if 'credits_' in key:
            package_name = key.replace('credits_', '').title()
            mapping_content += f'    "{key}": "{price_id}",  # {package_name}积分包\n'
    
    mapping_content += '}\n'
    
    # 保存到文件
    with open('stripe_price_mapping.py', 'w', encoding='utf-8') as f:
        f.write(mapping_content)
    
    print("✅ 价格映射已保存到 stripe_price_mapping.py")
    print("\n📋 请将生成的STRIPE_PRICE_IDS字典复制到 app/api/payments.py 文件中")

def main():
    print("🚀 开始设置Stripe产品和价格...")
    print(f"🔑 使用密钥: {stripe.api_key[:12]}...")
    
    try:
        # 创建订阅产品
        subscription_prices = create_subscription_products()
        
        # 创建积分包产品
        credit_prices = create_credit_products()
        
        # 合并所有价格
        all_prices = {**subscription_prices, **credit_prices}
        
        # 更新价格映射
        update_price_mapping(all_prices)
        
        print("\n🎉 Stripe产品设置完成！")
        print("\n📝 下一步：")
        print("1. 查看生成的 stripe_price_mapping.py 文件")
        print("2. 将STRIPE_PRICE_IDS字典复制到 app/api/payments.py")
        print("3. 重启后端服务器")
        print("4. 测试支付功能")
        
    except Exception as e:
        print(f"❌ 设置过程中出现错误: {str(e)}")
        print("请检查Stripe密钥是否正确配置")

if __name__ == "__main__":
    main()