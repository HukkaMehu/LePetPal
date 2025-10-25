from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Dog Monitor API"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    POSTGRES_USER: str = "dogmonitor"
    POSTGRES_PASSWORD: str = "dogmonitor"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "dogmonitor"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # S3/MinIO
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "dog-monitor"
    S3_REGION: str = "us-east-1"
    
    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"
    
    # Video Source
    # Can be:
    # - Integer (0, 1, 2) for local camera index
    # - URL (http://..., https://...) for remote camera stream
    VIDEO_SOURCE: str = "0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
