"""
GitHub Secrets Service
Handles encrypted secrets creation for GitHub repositories using the GitHub API.
Uses libsodium (PyNaCl) for encryption as required by GitHub's encrypted secrets API.
"""
import base64
from typing import Dict, Optional
import requests
from nacl import public, encoding
from app.config import settings
from app.logger import logger


class GitHubSecretsService:
    """Service for managing GitHub repository secrets"""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
    
    def _get_public_key(self, repo_full_name: str, github_token: str) -> Dict:
        """
        Get the repository's public key for encrypting secrets.
        
        Args:
            repo_full_name: Repository full name (e.g., "org/repo-name")
            github_token: GitHub personal access token
            
        Returns:
            Dictionary with 'key' and 'key_id' for encryption
        """
        url = f"{self.github_api_base}/repos/{repo_full_name}/actions/secrets/public-key"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get public key: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """
        Encrypt a secret value using the repository's public key.
        Uses libsodium sealed boxes as required by GitHub.
        
        Args:
            public_key: Base64-encoded public key from GitHub
            secret_value: Plain text secret value
            
        Returns:
            Base64-encoded encrypted secret
        """
        # Decode the public key
        public_key_bytes = base64.b64decode(public_key)
        sealed_box = public.SealedBox(public.PublicKey(public_key_bytes))
        
        # Encrypt the secret
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        
        # Return base64 encoded
        return base64.b64encode(encrypted).decode("utf-8")
    
    def create_secret(
        self,
        repo_full_name: str,
        secret_name: str,
        secret_value: str,
        github_token: str
    ) -> Dict:
        """
        Create or update a GitHub Actions secret in a repository.
        
        Args:
            repo_full_name: Repository full name (e.g., "org/repo-name")
            secret_name: Name of the secret (e.g., "DATABASE_URL")
            secret_value: Plain text value of the secret
            github_token: GitHub personal access token with repo scope
            
        Returns:
            Dictionary with creation result
        """
        logger.info(f"Creating secret '{secret_name}' in repository {repo_full_name}")
        
        # Get the public key for encryption
        key_data = self._get_public_key(repo_full_name, github_token)
        
        # Encrypt the secret
        encrypted_value = self._encrypt_secret(key_data["key"], secret_value)
        
        # Create/update the secret
        url = f"{self.github_api_base}/repos/{repo_full_name}/actions/secrets/{secret_name}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": key_data["key_id"]
        }
        
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code not in [201, 204]:
            raise Exception(f"Failed to create secret: {response.status_code} - {response.text}")
        
        logger.info(f"Successfully created secret '{secret_name}' in {repo_full_name}")
        return {"secret_name": secret_name, "created": True}
    
    def create_secrets_from_pulumi_outputs(
        self,
        repo_full_name: str,
        pulumi_outputs: Dict,
        github_token: str,
        secret_prefix: str = "",
        secret_mapping: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Create GitHub secrets from Pulumi stack outputs.
        
        Args:
            repo_full_name: Repository full name
            pulumi_outputs: Dictionary of Pulumi outputs (e.g., {"db_connection_string": "..."})
            github_token: GitHub token
            secret_prefix: Optional prefix for secret names (e.g., "PULUMI_")
            secret_mapping: Optional mapping from Pulumi output names to secret names
                           (e.g., {"db_connection_string": "DATABASE_URL"})
        
        Returns:
            Dictionary with created secrets info
        """
        if not pulumi_outputs:
            logger.warning("No Pulumi outputs to create secrets from")
            return {"secrets_created": [], "errors": []}
        
        created = []
        errors = []
        
        # Default mapping for common output names
        default_mapping = {
            "db_connection_string": "DATABASE_URL",
            "database_url": "DATABASE_URL",
            "service_account_key": "GCP_SA_KEY",
            "sa_key": "GCP_SA_KEY",
            "aws_access_key": "AWS_ACCESS_KEY_ID",
            "aws_secret_key": "AWS_SECRET_ACCESS_KEY",
            "redis_url": "REDIS_URL",
            "connection_string": "DATABASE_URL",
        }
        
        # Merge with provided mapping
        mapping = {**default_mapping, **(secret_mapping or {})}
        
        for output_name, output_value in pulumi_outputs.items():
            # Skip complex objects or None values
            if output_value is None or isinstance(output_value, (dict, list)):
                continue
            
            # Convert to string
            value_str = str(output_value)
            
            # Determine secret name
            if output_name in mapping:
                secret_name = mapping[output_name]
            else:
                # Convert to uppercase with prefix
                secret_name = f"{secret_prefix}{output_name.upper().replace('-', '_')}"
            
            try:
                self.create_secret(repo_full_name, secret_name, value_str, github_token)
                created.append({"output": output_name, "secret": secret_name})
                logger.info(f"Created secret {secret_name} from Pulumi output {output_name}")
            except Exception as e:
                error_msg = f"Failed to create secret {secret_name}: {str(e)}"
                logger.error(error_msg)
                errors.append({"output": output_name, "secret": secret_name, "error": str(e)})
        
        return {
            "secrets_created": created,
            "errors": errors,
            "total_created": len(created),
            "total_errors": len(errors)
        }
    
    def delete_secret(
        self,
        repo_full_name: str,
        secret_name: str,
        github_token: str
    ) -> bool:
        """
        Delete a GitHub Actions secret from a repository.
        
        Args:
            repo_full_name: Repository full name
            secret_name: Name of the secret to delete
            github_token: GitHub token
            
        Returns:
            True if deleted successfully
        """
        url = f"{self.github_api_base}/repos/{repo_full_name}/actions/secrets/{secret_name}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.delete(url, headers=headers, timeout=30)
        
        if response.status_code == 204:
            logger.info(f"Deleted secret '{secret_name}' from {repo_full_name}")
            return True
        elif response.status_code == 404:
            logger.warning(f"Secret '{secret_name}' not found in {repo_full_name}")
            return True  # Already gone
        else:
            raise Exception(f"Failed to delete secret: {response.status_code} - {response.text}")
    
    def list_secrets(self, repo_full_name: str, github_token: str) -> Dict:
        """
        List all secrets in a repository (names only, not values).
        
        Args:
            repo_full_name: Repository full name
            github_token: GitHub token
            
        Returns:
            Dictionary with list of secret names
        """
        url = f"{self.github_api_base}/repos/{repo_full_name}/actions/secrets"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Failed to list secrets: {response.status_code} - {response.text}")
        
        data = response.json()
        return {
            "total_count": data.get("total_count", 0),
            "secrets": [s["name"] for s in data.get("secrets", [])]
        }


# Singleton instance
github_secrets_service = GitHubSecretsService()
