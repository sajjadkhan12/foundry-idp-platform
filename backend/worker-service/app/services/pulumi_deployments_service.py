"""Pulumi Deployments API service for triggering infrastructure via Pulumi Cloud.

This service uses the Pulumi Cloud REST API to trigger deployments instead of 
running Pulumi locally. This offloads compute to Pulumi Cloud and enables 
massive scalability (hundreds of concurrent deployments).

API Docs: https://www.pulumi.com/docs/pulumi-cloud/deployments/api/
"""
import asyncio
import time
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import httpx
from app.config import settings
from app.logger import logger


class DeploymentOperation(str, Enum):
    """Supported Pulumi Deployment operations"""
    UPDATE = "update"
    PREVIEW = "preview"
    REFRESH = "refresh"
    DESTROY = "destroy"


class DeploymentStatus(str, Enum):
    """Pulumi Cloud deployment statuses"""
    NOT_STARTED = "not-started"
    ACCEPTED = "accepted"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class DeploymentResult:
    """Result from a Pulumi Cloud deployment"""
    deployment_id: str
    status: DeploymentStatus
    version: int
    outputs: Dict
    error: Optional[str] = None
    logs: Optional[str] = None


class PulumiDeploymentsService:
    """Service for triggering Pulumi deployments via the Pulumi Cloud REST API.
    
    This replaces the local Pulumi Automation API approach, enabling:
    - No local Pulumi CLI/SDK needed (saves ~1.5GB in container)
    - Unlimited concurrent deployments (Pulumi Cloud handles scaling)
    - Better reliability and managed execution environment
    """
    
    BASE_URL = "https://api.pulumi.com/api"
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, read=300.0)
    
    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """Get headers for Pulumi Cloud API requests"""
        return {
            "Authorization": f"token {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def trigger_deployment(
        self,
        organization: str,
        project: str,
        stack: str,
        operation: DeploymentOperation,
        git_repo_url: str,
        git_branch: str,
        git_repo_dir: str = "",
        config: Optional[Dict[str, str]] = None,
        esc_environment: Optional[str] = None,
        pre_run_commands: Optional[list] = None,
        access_token: Optional[str] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> DeploymentResult:
        """
        Trigger a deployment via Pulumi Cloud Deployments API.
        
        This sends a request to Pulumi Cloud which will:
        1. Clone the git repo on Pulumi's infrastructure
        2. Run the Pulumi operation (up/destroy/etc)
        3. Return results
        
        Args:
            organization: Pulumi organization name
            project: Pulumi project name
            stack: Pulumi stack name
            operation: Pulumi operation (update, destroy, preview, refresh)
            git_repo_url: URL of the git repository containing the Pulumi program
            git_branch: Git branch to deploy from (e.g., "refs/heads/main")
            git_repo_dir: Subdirectory in the repo containing the Pulumi program
            config: Pulumi configuration values to set
            esc_environment: ESC environment name for credentials (e.g., "org/gcp-production")
            pre_run_commands: Commands to run before Pulumi operation
            access_token: Pulumi access token (defaults to settings)
            on_output: Callback for log output
            
        Returns:
            DeploymentResult with status, outputs, and any errors
        """
        token = access_token or settings.PULUMI_ACCESS_TOKEN
        if not token:
            raise ValueError("PULUMI_ACCESS_TOKEN is required for Pulumi Deployments")
        
        # Prepare the deployment request payload
        payload = {
            "operation": operation.value,
            "inheritSettings": False,  # We provide all settings in the request
            "sourceContext": {
                "git": {
                    "repoURL": git_repo_url,
                    "branch": f"refs/heads/{git_branch}" if not git_branch.startswith("refs/") else git_branch,
                }
            },
            "operationContext": {
                "environmentVariables": {},
                "options": {
                    "skipInstallDependencies": False,
                    "deleteAfterDestroy": operation == DeploymentOperation.DESTROY
                }
            }
        }
        
        # Add repo directory if specified
        if git_repo_dir:
            payload["sourceContext"]["git"]["repoDir"] = git_repo_dir
        
        # Add pre-run commands (for installing deps, etc.)
        if pre_run_commands:
            payload["operationContext"]["preRunCommands"] = pre_run_commands
        else:
            # Default pre-run commands for Python projects
            payload["operationContext"]["preRunCommands"] = [
                "pip install -r requirements.txt"
            ]
        
        # Add ESC environment for credentials if provided
        if esc_environment:
            # ESC environments are linked via the oidc or environmentVariables
            # For ESC, we use the environment import syntax
            payload["operationContext"]["environmentVariables"]["PULUMI_ESC_ENV"] = esc_environment
        
        # Add Pulumi config values
        if config:
            # Config values are passed as environment variables or via preRunCommands
            # Pulumi Deployments uses stack config from the repo, but we can override via preRunCommands
            config_commands = []
            for key, value in config.items():
                if value is not None and value != "":
                    # Escape quotes in values
                    escaped_value = str(value).replace('"', '\\"')
                    config_commands.append(f'pulumi config set {key} "{escaped_value}" --non-interactive')
            
            if config_commands:
                existing_commands = payload["operationContext"].get("preRunCommands", [])
                # Add config commands before other pre-run commands
                payload["operationContext"]["preRunCommands"] = config_commands + existing_commands
        
        # Build the API URL
        url = f"{self.BASE_URL}/stacks/{organization}/{project}/{stack}/deployments"
        
        logger.info(f"[PulumiDeployments] Triggering {operation.value} for {organization}/{project}/{stack}")
        logger.info(f"[PulumiDeployments] Git source: {git_repo_url} @ {git_branch}")
        
        if on_output:
            on_output(f"Triggering {operation.value} deployment on Pulumi Cloud...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Trigger the deployment
                response = await client.post(
                    url,
                    headers=self._get_headers(token),
                    json=payload
                )
                
                if response.status_code == 404:
                    # Stack doesn't exist - we may need to create it first
                    logger.warning(f"[PulumiDeployments] Stack {organization}/{project}/{stack} not found, creating...")
                    await self._create_stack(client, token, organization, project, stack)
                    
                    # Retry the deployment
                    response = await client.post(
                        url,
                        headers=self._get_headers(token),
                        json=payload
                    )
                
                response.raise_for_status()
                result = response.json()
                
                deployment_id = result.get("id")
                version = result.get("version", 0)
                
                logger.info(f"[PulumiDeployments] Deployment triggered: ID={deployment_id}, Version={version}")
                
                if on_output:
                    on_output(f"Deployment triggered: ID={deployment_id}")
                
                # Poll for completion
                return await self._wait_for_completion(
                    client=client,
                    token=token,
                    organization=organization,
                    project=project,
                    stack=stack,
                    deployment_id=deployment_id,
                    version=version,
                    on_output=on_output
                )
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                logger.error(f"[PulumiDeployments] HTTP error: {e.response.status_code} - {error_detail}")
                return DeploymentResult(
                    deployment_id="",
                    status=DeploymentStatus.FAILED,
                    version=0,
                    outputs={},
                    error=f"API error: {e.response.status_code} - {error_detail}"
                )
            except Exception as e:
                logger.error(f"[PulumiDeployments] Error: {str(e)}")
                return DeploymentResult(
                    deployment_id="",
                    status=DeploymentStatus.FAILED,
                    version=0,
                    outputs={},
                    error=str(e)
                )
    
    async def _create_stack(
        self,
        client: httpx.AsyncClient,
        token: str,
        organization: str,
        project: str,
        stack: str
    ):
        """Create a new stack if it doesn't exist"""
        url = f"{self.BASE_URL}/stacks/{organization}/{project}/{stack}"
        
        try:
            response = await client.post(
                url,
                headers=self._get_headers(token),
                json={"stackName": f"{organization}/{project}/{stack}"}
            )
            response.raise_for_status()
            logger.info(f"[PulumiDeployments] Created stack: {organization}/{project}/{stack}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 409:  # 409 = already exists
                raise
            logger.info(f"[PulumiDeployments] Stack already exists: {organization}/{project}/{stack}")
    
    async def _wait_for_completion(
        self,
        client: httpx.AsyncClient,
        token: str,
        organization: str,
        project: str,
        stack: str,
        deployment_id: str,
        version: int,
        on_output: Optional[Callable[[str], None]] = None,
        poll_interval: int = 5,
        max_wait_time: int = 1800  # 30 minutes max
    ) -> DeploymentResult:
        """Poll for deployment completion and stream logs"""
        url = f"{self.BASE_URL}/stacks/{organization}/{project}/{stack}/deployments/{deployment_id}"
        logs_url = f"{url}/logs"
        
        start_time = time.time()
        last_log_token = None
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                logger.error(f"[PulumiDeployments] Deployment timed out after {max_wait_time}s")
                return DeploymentResult(
                    deployment_id=deployment_id,
                    status=DeploymentStatus.FAILED,
                    version=version,
                    outputs={},
                    error=f"Deployment timed out after {max_wait_time} seconds"
                )
            
            # Get deployment status
            try:
                response = await client.get(url, headers=self._get_headers(token))
                response.raise_for_status()
                deployment_data = response.json()
                
                status_str = deployment_data.get("status", "unknown")
                status = DeploymentStatus(status_str) if status_str in [s.value for s in DeploymentStatus] else DeploymentStatus.RUNNING
                
                logger.debug(f"[PulumiDeployments] Status: {status.value}")
                
                # Fetch and stream logs
                if on_output:
                    logs_params = {}
                    if last_log_token:
                        logs_params["continuationToken"] = last_log_token
                    
                    try:
                        logs_response = await client.get(
                            logs_url,
                            headers=self._get_headers(token),
                            params=logs_params
                        )
                        if logs_response.status_code == 200:
                            logs_data = logs_response.json()
                            for line in logs_data.get("lines", []):
                                log_line = line.get("line", "")
                                if log_line:
                                    on_output(log_line.rstrip())
                            last_log_token = logs_data.get("nextToken")
                    except Exception as log_error:
                        logger.debug(f"[PulumiDeployments] Log fetch error: {log_error}")
                
                # Check if deployment completed
                if status in [DeploymentStatus.SUCCEEDED, DeploymentStatus.FAILED, DeploymentStatus.CANCELED]:
                    outputs = {}
                    error = None
                    
                    if status == DeploymentStatus.SUCCEEDED:
                        # Fetch stack outputs
                        try:
                            outputs_url = f"{self.BASE_URL}/stacks/{organization}/{project}/{stack}/export"
                            outputs_response = await client.get(outputs_url, headers=self._get_headers(token))
                            if outputs_response.status_code == 200:
                                export_data = outputs_response.json()
                                # Extract outputs from stack state
                                deployment_state = export_data.get("deployment", {})
                                resources = deployment_state.get("resources", [])
                                for resource in resources:
                                    if resource.get("type") == "pulumi:pulumi:Stack":
                                        outputs = resource.get("outputs", {})
                                        break
                        except Exception as output_error:
                            logger.warning(f"[PulumiDeployments] Failed to fetch outputs: {output_error}")
                        
                        logger.info(f"[PulumiDeployments] Deployment succeeded with outputs: {list(outputs.keys())}")
                        if on_output:
                            on_output(f"Deployment completed successfully")
                    
                    elif status == DeploymentStatus.FAILED:
                        error = deployment_data.get("error", "Deployment failed")
                        logger.error(f"[PulumiDeployments] Deployment failed: {error}")
                        if on_output:
                            on_output(f"Deployment failed: {error}")
                    
                    elif status == DeploymentStatus.CANCELED:
                        error = "Deployment was canceled"
                        logger.warning(f"[PulumiDeployments] {error}")
                        if on_output:
                            on_output(error)
                    
                    return DeploymentResult(
                        deployment_id=deployment_id,
                        status=status,
                        version=version,
                        outputs=outputs,
                        error=error
                    )
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"[PulumiDeployments] Status check error: {e}")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def destroy_deployment(
        self,
        organization: str,
        project: str,
        stack: str,
        git_repo_url: str,
        git_branch: str,
        git_repo_dir: str = "",
        esc_environment: Optional[str] = None,
        access_token: Optional[str] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> DeploymentResult:
        """
        Trigger a destroy operation via Pulumi Cloud.
        
        This is a convenience wrapper around trigger_deployment with operation=destroy.
        """
        return await self.trigger_deployment(
            organization=organization,
            project=project,
            stack=stack,
            operation=DeploymentOperation.DESTROY,
            git_repo_url=git_repo_url,
            git_branch=git_branch,
            git_repo_dir=git_repo_dir,
            esc_environment=esc_environment,
            access_token=access_token,
            on_output=on_output,
        )
    
    def get_esc_environment(
        self,
        manifest: Optional[Dict],
        esc_env_aws: Optional[str] = None,
        esc_env_gcp: Optional[str] = None,
        esc_env_azure: Optional[str] = None
    ) -> Optional[str]:
        """
        Determine the appropriate ESC environment based on cloud provider from manifest.
        
        This is compatible with the existing PulumiService interface.
        """
        if not settings.PULUMI_USE_ESC:
            return None
        
        if not manifest:
            return None
        
        cloud_provider = manifest.get("cloud_provider", "").lower()
        
        # Use provided organization-specific values if available
        if any([esc_env_gcp, esc_env_aws, esc_env_azure]):
            if cloud_provider == "gcp":
                return esc_env_gcp
            elif cloud_provider == "aws":
                return esc_env_aws
            elif cloud_provider == "azure":
                return esc_env_azure
            return None
        
        # Fallback to settings
        if cloud_provider == "gcp" and settings.PULUMI_ESC_ENVIRONMENT_GCP:
            return settings.PULUMI_ESC_ENVIRONMENT_GCP
        elif cloud_provider == "aws" and settings.PULUMI_ESC_ENVIRONMENT_AWS:
            return settings.PULUMI_ESC_ENVIRONMENT_AWS
        elif cloud_provider == "azure" and settings.PULUMI_ESC_ENVIRONMENT_AZURE:
            return settings.PULUMI_ESC_ENVIRONMENT_AZURE
        
        return None


# Singleton instance
pulumi_deployments_service = PulumiDeploymentsService()
