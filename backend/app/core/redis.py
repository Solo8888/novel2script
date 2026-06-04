from typing import Optional
from redis.asyncio import from_url, Redis
from app.core import settings, log

_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """获取 Redis 连接（依赖注入）"""
    global _redis_client
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


async def init_redis() -> None:
    """初始化 Redis 连接池并测试连接"""
    global _redis_client
    if _redis_client is not None:
        return
    
    _redis_client = from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=5,
        socket_timeout=10,
    )
    # 初始化时测试连接
    await _redis_client.ping()
    log.info("Redis initialized successfully")


async def close_redis() -> None:
    """关闭 Redis 连接池"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        log.info("Redis connection pool closed")
