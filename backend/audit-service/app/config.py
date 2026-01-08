"""Configuration for audit microservice"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Audit Microservice"
    DEBUG: bool = True
    
    # Database (separate audit database)
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    
    # gRPC Server
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50057
    
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
