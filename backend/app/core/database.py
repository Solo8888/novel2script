from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出 pool_size 后额外允许的连接数
    pool_timeout=30,  # 获取连接的超时时间（秒）
    pool_recycle=3600,  # 连接回收时间（秒），避免长时间空闲连接
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 使用此设置时，业务代码中可能需要显式 refresh 对象
)

# 基类
Base = declarative_base()


async def get_db():
    """
    依赖注入：获取数据库会话
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
