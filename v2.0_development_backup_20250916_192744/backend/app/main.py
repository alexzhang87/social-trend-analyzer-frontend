from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import exception handlers
from .core.exceptions import (
    TrendAnalyzerException,
    trend_analyzer_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# All environment loading is now handled centrally in core.config
from .api import trends, health, seed, reports, debug, auth, admin, credits, feedback, google_trends, monkeylearn, data_studio, metabase, payments, cache, cache_optimization, monitoring, documentation, analysis, pmf, founder
from .api.v1 import websocket, optimization, mobile
from .api import social_scraping
from .core.config import settings
from .core.monitoring import PerformanceMiddleware
from .data.models.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    logger.info("INFO:     Creating database and tables...")
    try:
        create_db_and_tables()
        logger.info("INFO:     Database and tables created successfully")
        
        # 创建默认管理员用户（如果不存在）
        from .data.models.database import SessionLocal, User, UserRole, SubscriptionTier
        from .core.auth import get_password_hash
        from .core.config import settings
        
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
                    subscription_tier=SubscriptionTier.PRO
                )
                db.add(default_admin)
                db.commit()
                logger.info(f"INFO:     Default admin user created: {settings.ADMIN_EMAIL}")
            else:
                logger.info("INFO:     Admin user already exists")
        except Exception as e:
            logger.error(f"ERROR:     Failed to create admin user: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"ERROR:     Failed to create database and tables: {e}")
        raise
    yield
    # Code to run on shutdown
    logger.info("INFO:     Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
# In a production environment, you should restrict the origins to your frontend's domain
# For example: origins=["https://your-frontend-domain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# 添加性能监控中间件
app.add_middleware(PerformanceMiddleware)

# 注册异常处理器
app.add_exception_handler(TrendAnalyzerException, trend_analyzer_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

api_prefix = settings.API_V1_STR
app.include_router(health.router, prefix=f"{api_prefix}/health", tags=["health"])
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["authentication"])
app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["admin"])  # 添加管理员路由
app.include_router(trends.router, prefix=f"{api_prefix}/trends", tags=["trends"], include_in_schema=True)
app.include_router(analysis.router, prefix=f"{api_prefix}/analysis", tags=["analysis"])  # 添加分析路由
app.include_router(seed.router, prefix=f"{api_prefix}/seed", tags=["seed"])
app.include_router(reports.router, prefix=f"{api_prefix}/reports", tags=["reports"])
app.include_router(debug.router, prefix=f"{api_prefix}/debug", tags=["debug"])
app.include_router(credits.router, tags=["credits"])
app.include_router(feedback.router)  # 添加反馈路由
app.include_router(google_trends.router, prefix=f"{api_prefix}/google-trends", tags=["Google Trends"])  # 启用Google Trends
app.include_router(monkeylearn.router, prefix=f"{api_prefix}/monkeylearn", tags=["MonkeyLearn"])  # 添加MonkeyLearn路由
app.include_router(data_studio.router, prefix=f"{api_prefix}/data-studio", tags=["Data Studio"])  # 添加Google Data Studio路由
app.include_router(metabase.router, prefix=f"{api_prefix}/metabase", tags=["Metabase"])  # 添加Metabase开源BI路由
app.include_router(payments.router)  # 添加支付路由
app.include_router(cache.router, prefix=f"{api_prefix}/cache", tags=["cache"])  # 添加缓存管理路由
app.include_router(cache_optimization.router, prefix=f"{api_prefix}/cache-optimization", tags=["cache-optimization"])  # 添加缓存优化路由
app.include_router(monitoring.router, prefix=f"{api_prefix}/monitoring", tags=["monitoring"])  # 添加监控路由
app.include_router(documentation.router, prefix=f"{api_prefix}/docs", tags=["documentation"])  # 添加文档路由
app.include_router(websocket.router, prefix=f"{api_prefix}", tags=["websocket"])  # 添加WebSocket路由
app.include_router(optimization.router, prefix=f"{api_prefix}", tags=["optimization"])  # 添加数据优化路由
app.include_router(mobile.router, prefix=f"{api_prefix}/mobile", tags=["mobile"])  # 添加移动端路由
app.include_router(pmf.router, prefix=f"{api_prefix}/pmf", tags=["pmf"])  # 添加PMF路由
app.include_router(founder.router, prefix=f"{api_prefix}/founder", tags=["founder"])  # 添加创始人工具路由
app.include_router(social_scraping.router)  # 社交媒体抓取路由

@app.get("/")
async def root():
    return {"message": "Welcome to the Trend Analyzer API"}