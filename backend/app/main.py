from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# All environment loading is now handled centrally in core.config
from .api import trends, health, seed, analysis
from .core.config import settings
from .data.models.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    # Code to run on shutdown
    print("INFO:     Shutting down...")

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

api_prefix = settings.API_V1_STR
app.include_router(health.router, prefix=f"{api_prefix}/health", tags=["health"])
app.include_router(trends.router, prefix=f"{api_prefix}/analyze-trends", tags=["trends"])
app.include_router(seed.router, prefix=f"{api_prefix}/seed", tags=["seed"])
app.include_router(analysis.router, prefix=f"{api_prefix}/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Trend Analyzer API"}
