from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "DevPlatform IDP"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Admin credentials
    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    # Plugin system
    PLUGINS_STORAGE_PATH: str = "./storage/plugins"
    ENCRYPTION_KEY: str = "" 
    PULUMI_CONFIG_PASSPHRASE: str = "default-passphrase"  # SECURITY: Change this in production!
    PULUMI_ACCESS_TOKEN: str = ""  # Pulumi Cloud access token (optional, for cloud backend)
    PULUMI_ORG: str = ""  # Pulumi organization name (required when using Pulumi Cloud)
    # Pulumi ESC (Environments, Secrets, and Configuration) Configuration
    # ESC environments automatically handle OIDC token exchange for cloud credentials
    PULUMI_ESC_ENVIRONMENT_GCP: str = ""  # ESC environment for GCP (e.g., "Sajjadkhan12/gcp-production")
    PULUMI_ESC_ENVIRONMENT_AWS: str = ""  # ESC environment for AWS (e.g., "Sajjadkhan12/aws-production")
    PULUMI_ESC_ENVIRONMENT_AZURE: str = ""  # ESC environment for Azure (e.g., "Sajjadkhan12/azure-production")
    PULUMI_USE_ESC: bool = True  # Use ESC for credential management (required)
    
    # GitOps Configuration
    GITHUB_REPOSITORY: str = ""  # Base GitHub repository URL (can be overridden per plugin)
    GITHUB_TOKEN: str = ""  # GitHub personal access token for authentication
    GIT_WORK_DIR: str = "./storage/git-repos"  # Local directory for Git clones
    
    # Microservice Template Configuration
    GITHUB_TEMPLATE_REPO_URL: str = "https://github.com/sajjadkhan-academy/idp-templates.git"  # Template repository URL
    GITHUB_WEBHOOK_SECRET: str = ""  # Secret for verifying GitHub webhook signatures
    WEBHOOK_BASE_URL: str = ""  # Base URL for webhook endpoints (e.g., "https://your-domain.com")
    MICROSERVICE_REPO_ORG: str = ""  # Optional: Organization name for creating repos (empty = user's account)
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    BACKEND_CORS_ORIGINS: List[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS string into list if BACKEND_CORS_ORIGINS is empty
        if not self.BACKEND_CORS_ORIGINS and self.CORS_ORIGINS:
            self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # AWS Configuration (for cost services and other operations)
    AWS_REGION: str = "us-east-1"  # AWS region for operations
    
    # GCP Configuration (for cost services and other operations)
    GCP_PROJECT_ID: str = ""  # Project ID for API calls
    GCP_BILLING_ACCOUNT_ID: str = ""  # Optional billing account ID for cost queries
    
    model_config = ConfigDict(
        # Look for .env file in the backend directory (parent of app/)
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )

settings = Settings()
