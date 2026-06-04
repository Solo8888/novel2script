from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
from app.core import settings, log, init_redis, close_redis, get_redis
from app.core.database import get_db, engine
from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    log.info(f"Application {settings.APP_NAME} starting...")
    log.debug(f"Debug mode: {settings.DEBUG}")
    
    # 启动时初始化 Redis
    try:
        await init_redis()
        log.info("Redis connection successful")
    except Exception as e:
        log.warning(f"Redis connection failed on startup: {e}")
    
    # 启动时测试数据库连接
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            log.info("Database connection successful")
    except Exception as e:
        log.warning(f"Database connection failed on startup: {e}")
    
    yield
    
    # 关闭时优雅地关闭 Redis 和数据库引擎
    log.info("Closing Redis connection pool...")
    await close_redis()
    log.info("Disposing database connections...")
    await engine.dispose()
    log.info("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])


@app.get("/health")
async def health():
    log.debug("Health check endpoint called")
    return {"status": "ok", "app_name": settings.APP_NAME}


@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    """
    测试数据库连接
    """
    try:
        await db.execute(text("SELECT 1"))
        log.info("Database check successful")
        return {"database": "connected"}
    except Exception as e:
        log.error(f"Database check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"database": "disconnected", "reason": str(e)}
        )


@app.get("/redis-check")
async def redis_check(redis: Redis = Depends(get_redis)):
    """
    测试 Redis 连接
    """
    try:
        await redis.ping()
        log.info("Redis check successful")
        return {"redis": "pong"}
    except Exception as e:
        log.error(f"Redis check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"redis": "disconnected", "reason": str(e)}
        )


if settings.DEBUG:
    @app.get("/config/debug")
    async def debug_config():
        return {
            "APP_NAME": settings.APP_NAME,
            "DEBUG": settings.DEBUG,
            "DATABASE_URL": "***REDACTED***",
            "REDIS_URL": "***REDACTED***",
            "JWT_ALGORITHM": settings.JWT_ALGORITHM,
            "JWT_EXPIRE_MINUTES": settings.JWT_EXPIRE_MINUTES,
            "LLM_MOCK_MODE": settings.LLM_MOCK_MODE,
            "CORS_ORIGINS": settings.CORS_ORIGINS
        }

