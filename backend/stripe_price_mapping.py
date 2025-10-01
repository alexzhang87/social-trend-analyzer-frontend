# Stripe价格ID映射
# 这个文件由setup_stripe_products.py自动生成
# 请将这些价格ID复制到payments.py中的STRIPE_PRICE_IDS字典

STRIPE_PRICE_IDS = {
    # 订阅计划价格ID（月付）
    "starter_monthly": "price_1SCXv8LSYcMrFhJ2ZL5hJDm3",  # Starter计划
    "pro_monthly": "price_1SCXv9LSYcMrFhJ2iYdoc9V4",  # Pro计划
    "plus_monthly": "price_1SCXvALSYcMrFhJ2nN15UUTJ",  # Plus计划
    "enterprise_monthly": "price_1SCXvALSYcMrFhJ2nYDD7qor",  # Enterprise计划

    # 积分包价格ID（一次性购买）
    "credits_small": "price_1SCXvBLSYcMrFhJ2w6VQEzhp",  # Small积分包
    "credits_medium": "price_1SCXvBLSYcMrFhJ2G2YYw6dj",  # Medium积分包
    "credits_large": "price_1SCXvCLSYcMrFhJ2Ahz6ac8r",  # Large积分包
}
