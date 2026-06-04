from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Novel2Script"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./novel2script.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DEEPSEEK_API_KEY: str = ""
    LLM_MOCK_MODE: bool = True
    
    CORS_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
