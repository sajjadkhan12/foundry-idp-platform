"""Configuration for auth microservice"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth Microservice"
    DEBUG: bool = True
    
    # Database (shared with monolith)
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # gRPC Server
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051
    
    # Encryption (for credentials)
    ENCRYPTION_KEY: str = ""  # Optional, will generate in dev if not set
    
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
