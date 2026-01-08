"""Configuration for plugin microservice"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Plugin Microservice"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://default_user:default_password@postgres:5432/devplatform_idp"
    
    # gRPC Server
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50053
    
    # Storage
    PLUGINS_STORAGE_PATH: str = "/app/storage/plugins"
    
    # GitOps
    GITHUB_REPOSITORY: str = ""
    GITHUB_TOKEN: str = ""
    GIT_WORK_DIR: str = "/app/storage/git-repos"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True


settings = Settings()
