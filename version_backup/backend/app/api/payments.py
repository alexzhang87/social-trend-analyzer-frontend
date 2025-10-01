"""支付处理API模块"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Header
from sqlalchemy.orm import Session
from typing import Dict, Any
import stripe
import logging
from datetime import datetime, timedelta

from ..data.models.database import get_db, User, CreditTransaction, SubscriptionTier
from ..core.auth import get_current_active_user
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# 初始化Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    logger.warning("Stripe密钥未配置，支付功能将无法使用")

# 定义产品和价格ID映射（需要在Stripe仪表板中创建）
# TODO: 使用在Stripe仪表板中创建的实际价格ID替换以下占位符
STRIPE_PRICE_IDS = {
    "starter_monthly": "price_starter_monthly_placeholder",  # 替换为实际的Starter计划价格ID
    "pro_monthly": "price_pro_monthly_placeholder",          # 替换为实际的Pro计划价格ID
    "credits_small": "price_credits_small_placeholder",     # 替换为实际的小包装积分价格ID
    "credits_medium": "price_credits_medium_placeholder",   # 替换为实际的中包装积分价格ID
    "credits_large": "price_credits_large_placeholder"      # 替换为实际的大包装积分价格ID
}

@router.post("/create-checkout-session")
async def create_checkout_session(
    product_type: str = Body(..., embed=True),  # "subscription" 或 "credits"
    product_id: str = Body(..., embed=True),    # 具体的产品ID
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建Stripe结账会话"""
    try:
        if product_type == "subscription":
            # 订阅产品
            if product_id not in ["starter", "pro"]:
                raise HTTPException(status_code=400, detail="无效的订阅类型")
            
            price_id = STRIPE_PRICE_IDS.get(f"{product_id}_monthly")
            if not price_id:
                raise HTTPException(status_code=500, detail="价格ID未配置")
            
            # 创建结账会话
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{settings.FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/pricing",
                client_reference_id=str(current_user.id),
                customer_email=current_user.email,
                metadata={
                    'user_id': str(current_user.id),
                    'product_type': product_type,
                    'product_id': product_id
                }
            )
            
        elif product_type == "credits":
            # 积分包产品
            if product_id not in ["small", "medium", "large"]:
                raise HTTPException(status_code=400, detail="无效的积分包类型")
            
            price_id = STRIPE_PRICE_IDS.get(f"credits_{product_id}")
            if not price_id:
                raise HTTPException(status_code=500, detail="价格ID未配置")
            
            # 创建结账会话
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/credits",
                client_reference_id=str(current_user.id),
                customer_email=current_user.email,
                metadata={
                    'user_id': str(current_user.id),
                    'product_type': product_type,
                    'product_id': product_id
                }
            )
        else:
            raise HTTPException(status_code=400, detail="无效的产品类型")
        
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        logger.error(f"创建结账会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建结账会话失败: {str(e)}")

@router.post("/webhook")
async def stripe_webhook(
    payload: Dict[Any, Any],
    sig_header: str = Header(None),
    db: Session = Depends(get_db)
):
    """处理Stripe Webhook事件"""
    try:
        # 验证Webhook签名
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # 无效载荷
        logger.error(f"无效的Webhook载荷: {str(e)}")
        raise HTTPException(status_code=400, detail="无效的载荷")
    except stripe.error.SignatureVerificationError as e:
        # 无效签名
        logger.error(f"无效的Webhook签名: {str(e)}")
        raise HTTPException(status_code=400, detail="无效的签名")
    
    # 处理事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # 获取用户信息
        user_id = int(session['client_reference_id'])
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"未找到用户: {user_id}")
            raise HTTPException(status_code=404, detail="用户未找到")
        
        # 获取元数据
        metadata = session.get('metadata', {})
        product_type = metadata.get('product_type')
        product_id = metadata.get('product_id')
        
        if product_type == 'subscription':
            # 处理订阅支付完成
            await handle_subscription_payment(user, product_id, db)
        elif product_type == 'credits':
            # 处理积分包支付完成
            await handle_credits_payment(user, product_id, db)
    
    return {"status": "success"}

async def handle_subscription_payment(user: User, product_id: str, db: Session):
    """处理订阅支付"""
    try:
        # 更新用户订阅信息
        if product_id == "starter":
            new_tier = SubscriptionTier.STARTER
        elif product_id == "pro":
            new_tier = SubscriptionTier.PRO
        else:
            logger.error(f"无效的订阅产品ID: {product_id}")
            return
        
        # 更新用户订阅信息
        user.subscription_tier = new_tier
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        
        # 为新订阅添加积分
        monthly_credits = 0
        if new_tier == SubscriptionTier.STARTER:
            monthly_credits = 25
        elif new_tier == SubscriptionTier.PRO:
            monthly_credits = 60
            
        user.credits_balance += monthly_credits
        
        # 记录交易
        transaction = CreditTransaction(
            user_id=user.id,
            amount=monthly_credits,
            description=f"订阅{new_tier.value}套餐，获得{monthly_credits}积分",
            transaction_type="subscription"
        )
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"用户{user.email}订阅{new_tier.value}套餐成功")
        
    except Exception as e:
        logger.error(f"处理订阅支付失败: {str(e)}")
        db.rollback()

async def handle_credits_payment(user: User, product_id: str, db: Session):
    """处理积分包支付"""
    try:
        # 定义积分包配置
        credit_packages = {
            "small": {"credits": 10, "description": "小包装积分"},
            "medium": {"credits": 30, "description": "中包装积分"},
            "large": {"credits": 75, "description": "大包装积分"}
        }
        
        if product_id not in credit_packages:
            logger.error(f"无效的积分包ID: {product_id}")
            return
        
        package_config = credit_packages[product_id]
        credits_amount = package_config["credits"]
        description = package_config["description"]
        
        # 更新用户积分
        user.credits_balance += credits_amount
        
        # 记录交易
        transaction = CreditTransaction(
            user_id=user.id,
            amount=credits_amount,
            description=f"购买{description}，获得{credits_amount}积分",
            transaction_type="purchase",
            expires_at=datetime.utcnow() + timedelta(days=180)  # 积分有效期180天
        )
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"用户{user.email}购买{description}成功")
        
    except Exception as e:
        logger.error(f"处理积分包支付失败: {str(e)}")
        db.rollback()