"""Git service for GitOps workflow"""
import os
import shutil
import re
from pathlib import Path
from typing import Optional
import logging

try:
    import git
    from git import Repo
except ImportError:
    git = None
    Repo = None

from app.config import settings

logger = logging.getLogger(__name__)


class GitService:
    """Service for Git operations in GitOps workflow"""
    
    def __init__(self):
        self.work_dir = Path(settings.GIT_WORK_DIR)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.github_token = settings.GITHUB_TOKEN
    
    def get_github_token(self, organization_id: Optional[str] = None, business_unit_id: Optional[str] = None) -> str:
        """
        Get GitHub token with fallback: BU -> Org -> System
        
        Args:
            organization_id: Optional organization ID
            business_unit_id: Optional business unit ID
        
        Returns:
            GitHub token string
        """
        if organization_id:
            # Note: Plugin service would need to call auth-service via gRPC
            # For now, fallback to system default
            # TODO: Implement gRPC call to auth-service ConfigurationService
            pass
        
        # Fallback to system default
        return self.github_token
    
    def _get_authenticated_url(self, repo_url: str, token: Optional[str] = None) -> str:
        """Convert repo URL to authenticated HTTPS URL if token is available"""
        # If a token is provided (org-specific), use it. Otherwise fallback to system default.
        auth_token = token if token is not None else self.github_token
        if not auth_token:
            return repo_url
        
        if repo_url.startswith("https://github.com/"):
            url = repo_url.replace("https://", f"https://{auth_token}@")
            return url
        elif repo_url.startswith("git@github.com:"):
            url = repo_url.replace("git@github.com:", f"https://{auth_token}@github.com/")
            return url
        elif not repo_url.startswith("http") and not repo_url.startswith("git@") and "/" in repo_url:
            # Handle short format "org/repo"
            return f"https://{auth_token}@github.com/{repo_url}"
        else:
            return repo_url
    
    def initialize_and_push_plugin(
        self,
        repo_url: str,
        branch: str,
        source_dir: Path,
        commit_message: str = "Initial plugin upload",
        token: Optional[str] = None
    ) -> None:
        """
        Initialize repository, create branch, copy files, and push to GitHub
        """
        if git is None or Repo is None:
            raise ImportError("GitPython is not installed")
        
        import tempfile
        
        temp_repo_dir = None
        try:
            temp_repo_dir = Path(tempfile.mkdtemp(prefix="plugin_upload_"))
            
            auth_url = self._get_authenticated_url(repo_url, token)
            try:
                repo = Repo.clone_from(auth_url, str(temp_repo_dir), depth=1)
                logger.info(f"Cloned repository to {temp_repo_dir}")
            except Exception as e:
                logger.warning(f"Clone failed ({e}), initializing new repo")
                repo = Repo.init(str(temp_repo_dir))
                if 'origin' not in [r.name for r in repo.remotes]:
                    repo.create_remote('origin', auth_url)
                else:
                    repo.remotes.origin.set_url(auth_url)
            
            # Checkout or create branch
            try:
                repo.git.checkout(branch)
                logger.info(f"Checked out existing branch: {branch}")
            except Exception:
                try:
                    repo.git.checkout('main')
                except:
                    try:
                        repo.git.checkout('master')
                    except:
                        pass
                repo.git.checkout('-b', branch)
                logger.info(f"Created new branch: {branch}")
            
            # Clear existing files
            for item in temp_repo_dir.iterdir():
                if item.name != '.git' and item.is_file():
                    item.unlink()
                elif item.name != '.git' and item.is_dir():
                    shutil.rmtree(item)
            
            # Copy files from source_dir
            for item in source_dir.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(source_dir)
                    dest_path = temp_repo_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            # Add and commit
            repo.git.add(A=True)
            if repo.is_dirty() or len(repo.untracked_files) > 0:
                repo.index.commit(
                    commit_message,
                    author=git.Actor("IDP System", "idp@system")
                )
                logger.info(f"Committed changes: {commit_message}")
            
            # Push branch
            origin = repo.remotes.origin
            try:
                origin.push(branch, force=False)
                logger.info(f"Pushed branch {branch} to remote")
            except Exception as push_error:
                logger.warning(f"Branch {branch} push failed ({push_error}), attempting force push")
                try:
                    origin.push(branch, force=True)
                    logger.info(f"Force pushed branch {branch} to remote")
                except Exception as force_error:
                    logger.error(f"Failed to push branch even with force: {force_error}")
                    raise Exception(f"Failed to push branch to GitHub: {force_error}")
            
            logger.info(f"Successfully pushed plugin to {repo_url} branch {branch}")
            
        except Exception as e:
            logger.error(f"Failed to initialize and push plugin: {e}", exc_info=True)
            raise
        finally:
            if temp_repo_dir and temp_repo_dir.exists():
                shutil.rmtree(temp_repo_dir, ignore_errors=True)
    
    def delete_branch(
        self,
        repo_url: str,
        branch: str,
        token: Optional[str] = None
    ) -> bool:
        """
        Delete a Git branch from the remote repository
        Returns True if successful, False otherwise
        """
        if git is None or Repo is None:
            logger.warning("GitPython is not installed, cannot delete branch")
            return False
        
        if not repo_url or not branch:
            logger.warning(f"Missing repo_url or branch: repo_url={repo_url}, branch={branch}")
            return False
        
        # Skip deletion for main/master branches for safety
        if branch.lower() in ['main', 'master', 'develop', 'development']:
            logger.warning(f"Skipping deletion of protected branch: {branch}")
            return False
        
        import tempfile
        
        temp_repo_dir = None
        try:
            temp_repo_dir = Path(tempfile.mkdtemp(prefix="plugin_delete_"))
            
            auth_url = self._get_authenticated_url(repo_url, token)
            
            try:
                # Clone repository
                repo = Repo.clone_from(auth_url, str(temp_repo_dir), depth=1)
                logger.info(f"Cloned repository to {temp_repo_dir} for branch deletion")
            except Exception as e:
                logger.error(f"Failed to clone repository for branch deletion: {e}")
                return False
            
            # Check if branch exists
            try:
                repo.git.branch('-r', '--list', f'origin/{branch}')
                branch_exists = any(f'origin/{branch}' in line for line in repo.git.branch('-r', '--list').split('\n'))
            except Exception:
                branch_exists = False
            
            if not branch_exists:
                logger.info(f"Branch {branch} does not exist in remote, skipping deletion")
                return True
            
            # Delete branch from remote
            try:
                # Use git push with delete syntax: git push origin :refs/heads/<branch>
                # Pushing an empty ref deletes the branch
                origin = repo.remotes.origin
                refspec = f':refs/heads/{branch}'
                origin.push(refspec)
                logger.info(f"Successfully deleted branch {branch} from {repo_url}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete branch {branch} from {repo_url}: {e}")
                # Try alternative method: git push origin --delete <branch>
                try:
                    repo.git.push('origin', '--delete', branch)
                    logger.info(f"Successfully deleted branch {branch} using --delete flag")
                    return True
                except Exception as e2:
                    logger.error(f"Failed to delete branch {branch} with --delete flag: {e2}")
                    return False
            
        except Exception as e:
            logger.error(f"Error deleting branch {branch}: {e}", exc_info=True)
            return False
        finally:
            if temp_repo_dir and temp_repo_dir.exists():
                shutil.rmtree(temp_repo_dir, ignore_errors=True)


# Singleton instance
git_service = GitService()
