"""Configuration for worker microservice"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Worker Microservice"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://default_user:default_password@postgres:5432/devplatform_idp"
    
    # gRPC Server
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50054
    
    # Storage
    PLUGINS_STORAGE_PATH: str = "/app/storage/plugins"
    GIT_WORK_DIR: str = "/app/storage/git-repos"
    
    # Pulumi
    PULUMI_CONFIG_PASSPHRASE: str = "default-passphrase"
    PULUMI_ACCESS_TOKEN: str = ""
    PULUMI_ORG: str = ""
    PULUMI_ESC_ENVIRONMENT_AWS: str = ""
    PULUMI_ESC_ENVIRONMENT_GCP: str = ""
    PULUMI_ESC_ENVIRONMENT_AZURE: str = ""
    PULUMI_USE_ESC: bool = True
    
    # GitOps
    GITHUB_REPOSITORY: str = ""
    GITHUB_TOKEN: str = ""
    GITHUB_TEMPLATE_REPO_URL: str = ""
    MICROSERVICE_REPO_ORG: str = ""
    
    # Encryption
    ENCRYPTION_KEY: str = ""
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = True


settings = Settings()
