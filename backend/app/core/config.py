from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    APP_NAME: str = "Novel2Script"
    DEBUG: bool = True
    
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    DEEPSEEK_API_KEY: SecretStr = SecretStr("")
    LLM_MOCK_MODE: bool = True
    
    CORS_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
