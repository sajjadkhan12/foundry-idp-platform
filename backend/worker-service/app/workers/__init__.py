"""Worker module initialization - registers all Celery tasks"""
# Import logger early to configure logging (suppresses SQLAlchemy verbose logs)
import app.logger  # noqa: F401

from .config import create_celery_app
from app.tasks import infrastructure, microservice, cleanup

# Create Celery app
celery_app = create_celery_app()


@celery_app.task(name="provision_infrastructure", max_retries=0, bind=True)
def provision_infrastructure(self, job_id: str, plugin_id: str, version: str, inputs: dict,
                            credential_name: str = None, deployment_id: str = None):
    """Celery task wrapper for infrastructure provisioning"""
    from app.logger import logger
    logger.info(f"[CELERY TASK] Starting provision_infrastructure for job {job_id}")
    try:
        task = infrastructure.InfrastructureProvisionTask(job_id)
        result = task.execute(plugin_id, version, inputs, credential_name, deployment_id)
        logger.info(f"[CELERY TASK] provision_infrastructure completed for job {job_id}")
        return result
    except Exception as e:
        # Ensure error is handled even if task.execute doesn't catch it
        logger.error(f"[CELERY TASK ERROR] provision_infrastructure failed for job {job_id}: {str(e)}", exc_info=True)
        # The task's _handle_error should have already handled this, but re-raise to ensure Celery marks it as failed
        raise


@celery_app.task(name="destroy_infrastructure", max_retries=0, bind=True)
def destroy_infrastructure(self, deployment_id: str, job_id: str = None):
    """Celery task wrapper for infrastructure destruction"""
    from app.logger import logger
    logger.info(f"[CELERY TASK] Starting destroy_infrastructure for deployment {deployment_id} (job {job_id})")
    try:
        task = infrastructure.InfrastructureDestroyTask(deployment_id, job_id=job_id)
        result = task.execute()
        logger.info(f"[CELERY TASK] destroy_infrastructure completed for deployment {deployment_id}")
        return result
    except Exception as e:
        logger.error(f"[CELERY TASK ERROR] destroy_infrastructure failed for deployment {deployment_id}: {str(e)}", exc_info=True)
        raise


@celery_app.task(name="provision_microservice")
def provision_microservice(job_id: str, plugin_id: str, version: str, deployment_name: str,
                          user_id: str, deployment_id: str = None, inputs: dict = None):
    """Celery task wrapper for microservice provisioning"""
    task = microservice.MicroserviceProvisionTask(job_id)
    return task.execute(
        plugin_id=plugin_id,
        version=version,
        deployment_name=deployment_name,
        user_id=user_id,
        inputs=inputs,
        deployment_id=deployment_id
    )


@celery_app.task(name="destroy_microservice")
def destroy_microservice(deployment_id: str, job_id: str = None):
    """Celery task wrapper for microservice destruction"""
    task = microservice.MicroserviceDestroyTask(deployment_id, job_id=job_id)
    return task.execute()


@celery_app.task(name="cleanup_stuck_deployments")
def cleanup_stuck_deployments():
    """Celery task wrapper for cleanup stuck deployments"""
    return cleanup.cleanup_stuck_deployments()


@celery_app.task(name="cleanup_expired_refresh_tokens")
def cleanup_expired_refresh_tokens():
    """Celery task wrapper for cleanup expired refresh tokens"""
    return cleanup.cleanup_expired_refresh_tokens()


@celery_app.task(name="poll_github_actions_status")
def poll_github_actions_status():
    """Celery task wrapper for polling GitHub Actions status"""
    return cleanup.poll_github_actions_status()
