from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core import settings, log
from app.core.database import get_db, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    log.info(f"Application {settings.APP_NAME} starting...")
    log.debug(f"Debug mode: {settings.DEBUG}")
    
    # 启动时测试数据库连接
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            log.info("Database connection successful")
    except Exception as e:
        log.warning(f"Database connection failed on startup: {e}")
    
    yield
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

