import sys
from pathlib import Path
from loguru import logger
from .config import settings


def setup_logger():
    logger.remove()
    
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "novel2script_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    return logger


log = setup_logger()
