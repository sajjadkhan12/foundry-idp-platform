"""Pulumi Automation API service for executing infrastructure provisioning.

DEPRECATED: This service uses local Pulumi execution which requires the Pulumi SDK.
Use pulumi_deployments_service.py instead for production deployments.
"""
import os
import tempfile
import asyncio
import re
import time
from pathlib import Path
from typing import Dict, Optional

# Pulumi SDK is optional - only needed for fallback local execution
# For production, use Pulumi Deployments API instead
try:
    import pulumi
    from pulumi import automation as auto
    PULUMI_SDK_AVAILABLE = True
except ImportError:
    PULUMI_SDK_AVAILABLE = False
    pulumi = None
    auto = None

from app.config import settings
from app.logger import logger

class PulumiService:
    """Service for running Pulumi programs via Automation API"""
    
    def __init__(self):
        self.work_dir = Path(tempfile.gettempdir()) / "pulumi_workspaces"
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_pulumi(
        self,
        plugin_path: Path,
        stack_name: str,
        config: Dict[str, str],
        credentials: Optional[Dict] = None,
        project_name: str = "idp-plugin",
        manifest: Optional[Dict] = None,
        on_output: Optional[callable] = None,
        organization_id: Optional[str] = None,
        business_unit_id: Optional[str] = None
    ) -> Dict:
        """
        Execute a Pulumi program locally using the Automation API.
        
        DEPRECATED: Use pulumi_deployments_service.trigger_deployment() instead.
        This method requires the Pulumi SDK to be installed.
        
        Args:
            plugin_path: Path to extracted plugin directory
            stack_name: Name of the Pulumi stack
            config: Configuration dictionary
            credentials: Cloud credentials to inject
            project_name: Pulumi project name
        
        Returns:
            Dict with outputs and status
        """
        # Check if Pulumi SDK is available
        if not PULUMI_SDK_AVAILABLE:
            error_msg = (
                "Pulumi SDK is not installed. Local Pulumi execution is disabled. "
                "Please use GitOps flow with Pulumi Deployments API instead, or install "
                "pulumi, pulumi-aws, pulumi-gcp, pulumi-azure packages for local execution."
            )
            logger.error(f"[Pulumi] {error_msg}")
            return {
                "status": "failed",
                "error": error_msg,
                "outputs": {}
            }
        
        # Setup environment variables for cloud credentials
        env = os.environ.copy()
        
        # Get Pulumi configurations (with fallback: BU -> Org -> System)
        pulumi_access_token = None
        pulumi_org = None
        pulumi_esc_env_aws = None
        pulumi_esc_env_gcp = None
        pulumi_esc_env_azure = None
        
        if organization_id:
            # Try to get from auth-service
            from app.utils.config_helper import get_config_from_auth_service
            
            pulumi_access_token = await get_config_from_auth_service(
                organization_id, "PULUMI_ACCESS_TOKEN", business_unit_id
            )
            pulumi_org = await get_config_from_auth_service(
                organization_id, "PULUMI_ORG", business_unit_id
            )
            pulumi_esc_env_aws = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_AWS", business_unit_id
            )
            pulumi_esc_env_gcp = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_GCP", business_unit_id
            )
            pulumi_esc_env_azure = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_AZURE", business_unit_id
            )

            # Strict check: If tokens are missing for this organization, do NOT fallback
            if not pulumi_access_token:
                error_msg = f"PULUMI_ACCESS_TOKEN not configured for organization {organization_id}. Please set this in Settings."
                logger.error(f"[Pulumi] {error_msg}")
                raise ValueError(error_msg)
        else:
            # Fallback to system defaults ONLY if NO organization_id was provided (e.g., system-wide plugins if any)
            pulumi_access_token = settings.PULUMI_ACCESS_TOKEN
            pulumi_org = settings.PULUMI_ORG
            pulumi_esc_env_aws = settings.PULUMI_ESC_ENVIRONMENT_AWS
            pulumi_esc_env_gcp = settings.PULUMI_ESC_ENVIRONMENT_GCP
            pulumi_esc_env_azure = settings.PULUMI_ESC_ENVIRONMENT_AZURE
        
        # Configure Pulumi Cloud backend if access token is set
        use_pulumi_cloud = bool(pulumi_access_token)
        
        # Check if ESC environment is configured for this cloud provider
        esc_env = self.get_esc_environment(manifest, pulumi_esc_env_aws, pulumi_esc_env_gcp, pulumi_esc_env_azure)
        use_esc = esc_env is not None
        
        if use_pulumi_cloud:
            # Set Pulumi Cloud access token
            env["PULUMI_ACCESS_TOKEN"] = pulumi_access_token
            # Set organization if configured
            if pulumi_org:
                env["PULUMI_ORG"] = pulumi_org
            logger.info(f"[Pulumi] Using Pulumi Cloud backend (org: {pulumi_org or 'default'})")
        else:
            # Only set Pulumi passphrase for local secrets when not using Pulumi Cloud
            env["PULUMI_CONFIG_PASSPHRASE"] = settings.PULUMI_CONFIG_PASSPHRASE
        
        # ESC is required for credential management
        if not use_esc:
            cloud_provider = manifest.get("cloud_provider", "unknown").lower() if manifest else "unknown"
            error_msg = f"ESC environment not configured for {cloud_provider}. Please set PULUMI_ESC_ENVIRONMENT_{cloud_provider.upper()} in configuration."
            logger.error(f"[Pulumi] {error_msg}")
            raise ValueError(error_msg)
        
        # ESC environment will be linked to the stack after creation
        logger.info(f"[Pulumi] ESC environment configured: {esc_env} - will link to stack for credential management")
        
        # Create workspace
        workspace_dir = self.work_dir / stack_name
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create or select stack
            import sys
            
            # Configure secrets provider based on backend type
            secrets_provider = None if use_pulumi_cloud else "passphrase"
            
            # Create project settings
            project_settings = auto.ProjectSettings(
                name=project_name,
                runtime=auto.ProjectRuntimeInfo(
                    name="python",
                    options={"virtualenv": sys.prefix}
                )
            )
            
            # Create workspace options
            workspace_opts = auto.LocalWorkspaceOptions(
                env_vars=env,
                secrets_provider=secrets_provider,
                project_settings=project_settings
            )
            
            # Create or select stack (Pulumi Cloud backend is automatically used when PULUMI_ACCESS_TOKEN is set)
            stack = auto.create_or_select_stack(
                stack_name=stack_name,
                work_dir=str(plugin_path),
                opts=workspace_opts
            )
            
            # Link ESC environment to the stack for credential management
            if use_esc and esc_env:
                try:
                    # Link ESC environment to stack (note: variadic args, not a list)
                    stack.add_environments(esc_env)
                    logger.info(f"[Pulumi] Linked ESC environment '{esc_env}' to stack for credential management")
                except Exception as esc_error:
                    logger.error(f"[Pulumi] Failed to link ESC environment: {esc_error}")
                    raise ValueError(f"ESC environment linking failed: {esc_error}")
            
            # Log backend information
            if use_pulumi_cloud:
                logger.info(f"[Pulumi] Stack '{stack_name}' will use Pulumi Cloud backend")
            else:
                logger.info(f"[Pulumi] Stack '{stack_name}' will use local backend")
            
            # Set stack config
            # Skip None values and empty strings for optional fields
            for key, value in config.items():
                # Skip None, empty strings, and empty dicts/lists
                if value is None or value == "" or value == {} or value == []:
                    continue
                stack.set_config(key, auto.ConfigValue(value=str(value)))
            
            # Install provider plugin dynamically based on manifest
            if manifest:
                cloud_provider = manifest.get("cloud_provider", "").lower()
                provider_version = manifest.get("provider_version")  # Optional override
                
                # Default provider versions
                # Note: Pulumi plugin versions should be without 'v' prefix
                # Using recent stable versions that are confirmed to exist
                provider_versions = {
                    "gcp": "7.0.0",
                    "aws": "7.12.0",  # Updated to latest stable version
                    "azure": "5.0.0"
                }
                
                if cloud_provider in provider_versions:
                    version = provider_version or provider_versions[cloud_provider]
                    stack.workspace.install_plugin(cloud_provider, version)
                elif cloud_provider:
                    # Unknown provider, try to install with default version
                    version = provider_version or "latest"
                    stack.workspace.install_plugin(cloud_provider, version)
            else:
                # Fallback to GCP if no manifest provided
                stack.workspace.install_plugin("gcp", "v7.0.0")
            
            # Run pip install in the plugin directory
            await self._install_dependencies(plugin_path)
            
            # Perform the update
            up_result = stack.up(on_output=on_output or (lambda msg: logger.info(f"[Pulumi] {msg}")))
            
            # Get outputs
            outputs = {}
            for key, value in up_result.outputs.items():
                outputs[key] = value.value
            
            return {
                "status": "success",
                "outputs": outputs,
                "summary": {
                    "resources_created": up_result.summary.resource_changes.get("create", 0),
                    "resources_updated": up_result.summary.resource_changes.get("update", 0),
                }
            }
        
        except Exception as e:
            # Capture more details if it's a Pulumi error
            error_msg = str(e)
            if hasattr(e, 'stdout') and e.stdout:
                error_msg += f"\nstdout: {e.stdout}"
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f"\nstderr: {e.stderr}"
                
            return {
                "status": "failed",
                "error": error_msg,
                "outputs": {}
            }
    
    async def destroy_stack(
        self,
        plugin_path: Path,
        stack_name: str,
        credentials: Optional[Dict] = None,
        project_name: str = "idp-plugin",  # Changed to match run_pulumi default
        cloud_provider: Optional[str] = None,  # Optional cloud provider for ESC environment selection
        on_output: Optional[callable] = None,
        organization_id: Optional[str] = None,
        business_unit_id: Optional[str] = None
    ) -> Dict:
        """Destroy a Pulumi stack locally using the Automation API.
        
        DEPRECATED: Use pulumi_deployments_service.destroy_deployment() instead.
        """
        # Check if Pulumi SDK is available
        if not PULUMI_SDK_AVAILABLE:
            error_msg = (
                "Pulumi SDK is not installed. Local Pulumi execution is disabled. "
                "Please use GitOps flow with Pulumi Deployments API instead."
            )
            logger.error(f"[Pulumi] {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }
        
        import sys
        env = os.environ.copy()
        
        # Get Pulumi configurations (with fallback: BU -> Org -> System)
        pulumi_access_token = None
        pulumi_org = None
        pulumi_esc_env_aws = None
        pulumi_esc_env_gcp = None
        pulumi_esc_env_azure = None
        
        if organization_id:
            # Try to get from auth-service
            from app.utils.config_helper import get_config_from_auth_service
            
            pulumi_access_token = await get_config_from_auth_service(
                organization_id, "PULUMI_ACCESS_TOKEN", business_unit_id
            )
            pulumi_org = await get_config_from_auth_service(
                organization_id, "PULUMI_ORG", business_unit_id
            )
            pulumi_esc_env_aws = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_AWS", business_unit_id
            )
            pulumi_esc_env_gcp = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_GCP", business_unit_id
            )
            pulumi_esc_env_azure = await get_config_from_auth_service(
                organization_id, "PULUMI_ESC_ENVIRONMENT_AZURE", business_unit_id
            )

            # Strict check: If tokens are missing for this organization, do NOT fallback
            if not pulumi_access_token:
                error_msg = f"PULUMI_ACCESS_TOKEN not configured for organization {organization_id}. Please set this in Settings."
                logger.error(f"[Pulumi] {error_msg}")
                raise ValueError(error_msg)
        else:
            # Fallback to system defaults
            pulumi_access_token = settings.PULUMI_ACCESS_TOKEN
            pulumi_org = settings.PULUMI_ORG
            pulumi_esc_env_aws = settings.PULUMI_ESC_ENVIRONMENT_AWS
            pulumi_esc_env_gcp = settings.PULUMI_ESC_ENVIRONMENT_GCP
            pulumi_esc_env_azure = settings.PULUMI_ESC_ENVIRONMENT_AZURE
        
        # Configure Pulumi Cloud backend if access token is set
        use_pulumi_cloud = bool(pulumi_access_token)
        
        # Check if ESC environment is configured for this cloud provider
        # Create a minimal manifest-like dict for ESC lookup
        manifest = {"cloud_provider": cloud_provider.lower()} if cloud_provider and isinstance(cloud_provider, str) else None
        esc_env = self.get_esc_environment(manifest, pulumi_esc_env_aws, pulumi_esc_env_gcp, pulumi_esc_env_azure)
        use_esc = esc_env is not None
        
        if use_pulumi_cloud:
            # Set Pulumi Cloud access token
            env["PULUMI_ACCESS_TOKEN"] = pulumi_access_token
            # Set organization if configured
            if pulumi_org:
                env["PULUMI_ORG"] = pulumi_org
            logger.info(f"[Pulumi] Using Pulumi Cloud backend for destroy (org: {pulumi_org or 'default'})")
        else:
            # Only set Pulumi passphrase for local secrets when not using Pulumi Cloud
            env["PULUMI_CONFIG_PASSPHRASE"] = settings.PULUMI_CONFIG_PASSPHRASE
        
        # ESC is required for credential management when destroying a stack
        # Note: If cloud_provider is None/unknown, we may still want to attempt destroy
        # (e.g., for deployments that were never fully provisioned)
        if not use_esc and cloud_provider and cloud_provider.lower() != "unknown":
            cloud_provider_str = cloud_provider.lower()
            error_msg = f"ESC environment not configured for {cloud_provider_str}. Please set PULUMI_ESC_ENVIRONMENT_{cloud_provider_str.upper()} in configuration."
            logger.error(f"[Pulumi] {error_msg}")
            raise ValueError(error_msg)
        elif not use_esc:
            # If cloud_provider is unknown/None, log warning but continue (deployment may not have been provisioned)
            logger.warning(f"[Pulumi] ESC environment not configured for {cloud_provider or 'unknown'} cloud provider, but continuing with destroy attempt")
        
        # ESC environment will be linked to the stack after selection
        logger.info(f"[Pulumi] ESC environment configured: {esc_env} - will link to stack for destroy")
        
        try:
            # Configure secrets provider based on backend type
            secrets_provider = None if use_pulumi_cloud else "passphrase"
            
            # Create project settings
            project_settings = auto.ProjectSettings(
                name=project_name,
                runtime=auto.ProjectRuntimeInfo(
                    name="python",
                    options={"virtualenv": sys.prefix}
                )
            )
            logger.info(f"[Pulumi] Project settings created")
            
            # Create workspace options
            workspace_opts = auto.LocalWorkspaceOptions(
                env_vars=env,
                secrets_provider=secrets_provider,
                project_settings=project_settings
            )
            
            # First try to select the existing stack (from Pulumi Cloud or local)
            # This will work if the stack exists in Pulumi Cloud
            try:
                logger.info(f"[Pulumi] Selecting stack {stack_name} in {plugin_path}")
                stack = auto.select_stack(
                    stack_name=stack_name,
                    work_dir=str(plugin_path),
                    opts=workspace_opts
                )
                logger.info(f"[Pulumi] Stack selected")
                
                # Link ESC environment to the stack for credential management
                if use_esc and esc_env:
                    try:
                        # Link ESC environment to stack (note: variadic args, not a list)
                        stack.add_environments(esc_env)
                        logger.info(f"[Pulumi] Linked ESC environment '{esc_env}' to stack for destroy")
                    except Exception as esc_error:
                        logger.error(f"[Pulumi] Failed to link ESC environment: {esc_error}")
                        raise ValueError(f"ESC environment linking failed: {esc_error}")
                
                backend_type = "Pulumi Cloud" if use_pulumi_cloud else "local"
                logger.info(f"[Pulumi] Selected existing stack {stack_name} from {backend_type}")
            except Exception as select_error:
                # If select fails, try create_or_select (will create if doesn't exist)
                error_str = str(select_error).lower()
                if "no stack named" in error_str or "not found" in error_str:
                    logger.info(f"[Pulumi] Stack {stack_name} not found - may have been already deleted")
                    return {
                        "status": "success",
                        "summary": {},
                        "message": "Stack not found (may have been already deleted)"
                    }
                # For other errors, try create_or_select as fallback
                logger.warning(f"[Pulumi] Could not select stack, trying create_or_select: {select_error}")
                stack = auto.create_or_select_stack(
                    stack_name=stack_name,
                    work_dir=str(plugin_path),
                    opts=workspace_opts
                )
                
                # ESC environment is already set in env_vars if configured
            
            # Check if stack exists by trying to get its outputs
            try:
                # Try to refresh to ensure we have the latest state from Pulumi Cloud
                stack.refresh(on_output=on_output or (lambda msg: logger.info(f"[Pulumi] {msg}")))
                logger.info(f"[Pulumi] Stack {stack_name} found and refreshed")
            except Exception as refresh_error:
                error_str = str(refresh_error).lower()
                # If stack doesn't exist, that's okay - it might have been already deleted
                if "no stack named" in error_str or "not found" in error_str:
                    logger.info(f"[Pulumi] Stack {stack_name} not found - may have been already deleted")
                    return {
                        "status": "success",
                        "summary": {},
                        "message": "Stack not found (may have been already deleted)"
                    }
                else:
                    logger.warning(f"[Pulumi] Warning: Could not refresh stack: {refresh_error}")
                    # Continue anyway - try to destroy
            
            # Destroy the infrastructure first
            logger.info(f"[Pulumi] Destroying stack {stack_name}...")
            destroy_result = None
            destroy_success = False
            try:
                destroy_result = stack.destroy(on_output=on_output or (lambda msg: logger.info(f"[Pulumi] {msg}")))
                destroy_success = True
                logger.info(f"[Pulumi] All resources in stack {stack_name} destroyed successfully")
            except Exception as destroy_error:
                error_str = str(destroy_error).lower()
                # If stack doesn't exist or has no resources, that's okay
                if "no stack named" in error_str or "not found" in error_str:
                    logger.info(f"[Pulumi] Stack {stack_name} not found - may have been already deleted")
                    return {
                        "status": "success",
                        "summary": {},
                        "message": "Stack not found (may have been already deleted)"
                    }
                else:
                    # Destroy failed - don't remove stack, return error
                    logger.error(f"[Pulumi] ERROR: Destroy failed: {destroy_error}")
                    return {
                        "status": "failed",
                        "error": f"Failed to destroy resources: {str(destroy_error)}",
                        "summary": {}
                    }
            
            # Only remove the stack if destroy was successful (all resources deleted)
            if destroy_success:
                logger.info(f"[Pulumi] All resources deleted. Removing stack {stack_name}...")
                stack_removed = False
                try:
                    stack.workspace.remove_stack(stack_name)
                    logger.info(f"[Pulumi] Stack {stack_name} removed successfully")
                    stack_removed = True
                except Exception as remove_error:
                    error_str = str(remove_error).lower()
                    # Try alternative method using Pulumi CLI if API method fails
                    if "not found" not in error_str and "does not exist" not in error_str:
                        logger.warning(f"[Pulumi] API remove_stack failed, trying CLI method: {remove_error}")
                        try:
                            import subprocess
                            import sys
                            # Validate stack_name to prevent command injection
                            if not re.match(r'^[a-zA-Z0-9_-]+$', stack_name):
                                raise ValueError(f"Invalid stack name: {stack_name}")
                            
                            # Use pulumi stack rm command as fallback
                            result = subprocess.run(
                                [sys.executable, "-m", "pulumi", "stack", "rm", stack_name, "--yes"],
                                cwd=str(plugin_path),
                                env=env,
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            if result.returncode == 0:
                                logger.info(f"[Pulumi] Stack {stack_name} removed via CLI")
                                stack_removed = True
                            else:
                                logger.error(f"[Pulumi] CLI stack rm failed: {result.stderr}")
                        except Exception as cli_error:
                            logger.error(f"[Pulumi] CLI stack rm also failed: {cli_error}")
                    else:
                        logger.info(f"[Pulumi] Stack {stack_name} already removed or doesn't exist")
                        stack_removed = True  # Treat as success if it doesn't exist
                
                # Return success with stack removal status
                return {
                    "status": "success",
                    "summary": destroy_result.summary.resource_changes if destroy_result and hasattr(destroy_result, 'summary') else {},
                    "stack_removed": stack_removed,
                    "message": "Infrastructure destroyed and stack removed" if stack_removed else "Infrastructure destroyed but stack removal failed"
                }
            else:
                # Should not reach here, but just in case
                return {
                    "status": "failed",
                    "error": "Destroy did not complete successfully",
                    "stack_removed": False
                }
        except Exception as e:
            error_msg = str(e)
            # Check if error is "stack not found" - this is okay if stack was already deleted
            if "no stack named" in error_msg.lower() or "not found" in error_msg.lower():
                logger.info(f"[Pulumi] Stack {stack_name} not found - may have been already deleted")
                return {
                    "status": "success",
                    "summary": {},
                    "message": "Stack not found (may have been already deleted)"
                }
            
            return {
                "status": "failed",
                "error": error_msg
            }
    
    def get_esc_environment(
        self, 
        manifest: Optional[Dict],
        esc_env_aws: Optional[str] = None,
        esc_env_gcp: Optional[str] = None,
        esc_env_azure: Optional[str] = None
    ) -> Optional[str]:
        """
        Determine the appropriate ESC environment based on cloud provider from manifest.
        
        Args:
            manifest: Plugin manifest containing cloud_provider information
            
        Returns:
            ESC environment name (e.g., "Sajjadkhan12/gcp-production") or None if not configured
        """
        if not settings.PULUMI_USE_ESC:
            return None
        
        if not manifest:
            return None
        
        cloud_provider = manifest.get("cloud_provider", "").lower()
        
        # Use provided organization-specific values if available
        # These are passed from run_pulumi/destroy_stack which only use org configs if org_id is present
        if any([esc_env_gcp, esc_env_aws, esc_env_azure]):
            if cloud_provider == "gcp":
                return esc_env_gcp
            elif cloud_provider == "aws":
                return esc_env_aws
            elif cloud_provider == "azure":
                return esc_env_azure
            return None
            
        # Fallback to settings ONLY if no organization values were provided (system-level request)
        esc_env_gcp = settings.PULUMI_ESC_ENVIRONMENT_GCP
        esc_env_aws = settings.PULUMI_ESC_ENVIRONMENT_AWS
        esc_env_azure = settings.PULUMI_ESC_ENVIRONMENT_AZURE
        
        if cloud_provider == "gcp" and esc_env_gcp:
            return esc_env_gcp
        elif cloud_provider == "aws" and esc_env_aws:
            return esc_env_aws
        elif cloud_provider == "azure" and esc_env_azure:
            return esc_env_azure
        
        return None
    
    async def _install_dependencies(self, plugin_path: Path):
        """Install Python dependencies for the plugin"""
        import sys
        requirements_file = plugin_path / "requirements.txt"
        if requirements_file.exists():
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            logger.info(f"[PulumiService] Installing dependencies with command: {cmd}")
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    logger.error(f"[PulumiService] Pip install failed: {stderr.decode()}")
                    raise Exception(f"Pip install failed: {stderr.decode()}")
                logger.info(f"[PulumiService] Dependencies installed successfully")
            except Exception as e:
                logger.error(f"[PulumiService] Failed to run pip: {e}")
                raise e

# Singleton instance
pulumi_service = PulumiService()
