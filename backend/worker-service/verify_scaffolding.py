import sys
import os
import uuid
import asyncio
from unittest.mock import MagicMock, patch

# Add the app directory to sys.path
sys.path.append(os.getcwd())

# Ensure minimal environment variables if not present
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://default_user:default_password@postgres:5432/devplatform_idp"
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "test-secret"
if "PULUMI_CONFIG_PASSPHRASE" not in os.environ:
    os.environ["PULUMI_CONFIG_PASSPHRASE"] = "test"

from app.tasks.microservice import MicroserviceProvisionTask
from app.tasks.db import get_sync_db_session
from app.models import (
    User, Organization, Plugin, PluginVersion, Job, JobStatus,
    Deployment, DeploymentStatus, Environment
)
from app.models.deployment import DeploymentType

def setup_test_data():
    db = get_sync_db_session()
    try:
        # Check if org exists or create
        org = db.query(Organization).filter(Organization.name == "Scaffolding Test Org").first()
        if not org:
            org = Organization(id=uuid.uuid4(), name="Scaffolding Test Org", slug=f"scaffolding-test-org-{uuid.uuid4().hex[:4]}")
            db.add(org)
            db.commit()
            db.refresh(org)
        
        # Check if user exists or create
        user = db.query(User).filter(User.email == "scaffold-test@example.com").first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                username=f"scaffoldtest_{uuid.uuid4().hex[:4]}",
                email="scaffold-test@example.com",
                organization_id=org.id,
                hashed_password="...",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create dummy Plugin
        plugin_id = f"test-plugin-{uuid.uuid4().hex[:8]}"
        plugin = Plugin(
            id=plugin_id,
            name="Test Scaffolding Plugin",
            deployment_type="microservice"
        )
        db.add(plugin)
        
        # Create dummy PluginVersion
        pv = PluginVersion(
            plugin_id=plugin_id,
            version="1.0.0",
            template_repo_url="https://github.com/test/template",
            template_path="python-service",
            manifest={"cloud_provider": "kubernetes"}
        )
        db.add(pv)
        db.commit()
        db.refresh(pv)
        
        # Create dummy Job
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            plugin_version_id=pv.id,
            status=JobStatus.PENDING,
            triggered_by="scaffold-test@example.com"
        )
        db.add(job)
        
        db.commit()
        return job_id, plugin_id, user.id
    finally:
        db.close()

def run_verification():
    job_id, plugin_id, user_id = setup_test_data()
    print(f"Setup test data: Job ID {job_id}")
    
    # Patch the locations WHERE THEY ARE USED in app.tasks.microservice
    with patch('app.tasks.microservice.git_service.get_github_token') as mock_token, \
         patch('app.tasks.microservice.microservice_service.create_repository_from_template') as mock_create_repo, \
         patch('app.tasks.microservice.pulumi_service.run_pulumi') as mock_run_pulumi, \
         patch('app.services.github_secrets_service.GitHubSecretsService.create_secrets_from_pulumi_outputs') as mock_secrets, \
         patch('app.tasks.microservice.get_config_from_auth_service_sync') as mock_config_sync, \
         patch('app.tasks.microservice.create_notification_sync') as mock_notif:
        
        mock_token.return_value = "mock-github-token"
        mock_create_repo.return_value = ("https://github.com/org/repo-test", "org/repo-test")
        mock_config_sync.return_value = "test-org"
        
        # We need mock_run_pulumi to be an async mock
        async def async_success(*args, **kwargs):
            return {
                "status": "success",
                "outputs": {"DATABASE_URL": "mock-db-url-test"}
            }
        mock_run_pulumi.side_effect = async_success
        
        print(f"Executing MicroserviceProvisionTask({job_id}).execute...")
        task = MicroserviceProvisionTask(job_id)
        
        # Use a real user_id string
        task.execute(
            plugin_id=plugin_id,
            version="1.0.0",
            deployment_name=f"test-scaff-{uuid.uuid4().hex[:6]}",
            user_id=str(user_id),
            inputs={
                "target_cluster": "test-cluster-01",
                "namespace": "test-ns-01"
            }
        )
        
        print("Task execution finished. Verifying database state...")
        
        db = get_sync_db_session()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            print(f"Job Status: {job.status}")
            
            if job.status == JobStatus.FAILED:
                print(f"❌ Job failed with error: {job.error_message}")
            
            # Extract deployment_id from job outputs
            deployment_id = job.outputs.get('deployment_id') if job.outputs else None
            
            deployment = None
            if deployment_id:
                deployment = db.query(Deployment).filter(Deployment.id == uuid.UUID(deployment_id)).first()
            
            if deployment:
                print(f"✅ Deployment Created: {deployment.id}")
                print(f"✅ Deployment Name: {deployment.name}")
                print(f"✅ Deployment Status: {deployment.status}")
                print(f"✅ Deployment Stack: {deployment.stack_name}")
                print(f"✅ Deployment Repo: {deployment.github_repo_name}")
            else:
                # Try to find by name if not in outputs
                print("⚠️ Deployment ID not in job outputs, searching by name fallback...")
                
            if job.status == JobStatus.SUCCESS:
                print("✅ Job status is SUCCESS")
                print(f"mock_run_pulumi called: {mock_run_pulumi.called}")
                print(f"mock_secrets called: {mock_secrets.called}")
                
                if mock_run_pulumi.called and mock_secrets.called:
                    print("\nVerification successful!")
                else:
                    print("\nVerification FAILED: Some mocks were not called as expected.")
            else:
                print(f"❌ Verification FAILED: Job status is {job.status}")
        finally:
            db.close()

if __name__ == "__main__":
    run_verification()
