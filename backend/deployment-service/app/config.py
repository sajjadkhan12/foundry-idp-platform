"""Configuration for deployment microservice"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Deployment Microservice"
    DEBUG: bool = True
    
    # Database (shared with monolith)
    DATABASE_URL: str
    
    # gRPC Server
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50055
    
    # Worker Service (for triggering provisioning jobs)
    WORKER_SERVICE_URL: str = "worker-service:50054"
    
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
