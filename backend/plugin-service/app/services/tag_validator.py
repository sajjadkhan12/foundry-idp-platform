"""Tag validation service"""
import re
from typing import Dict, Tuple, Optional

REQUIRED_TAGS = {
    "team": "Team name (e.g., backend, frontend, data, platform)",
    "owner": "Owner email or username responsible for this deployment",
    "purpose": "Purpose of deployment (e.g., api, worker, storage, database)"
}

TAG_KEY_PATTERN = re.compile(r'^[a-z0-9-]+$')
TAG_VALUE_MAX_LENGTH = 255
RESERVED_PREFIXES = ['system-', 'Foundry-', 'internal-']


def validate_tags(tags: Dict[str, str], environment: str) -> Tuple[bool, Optional[str]]:
    """Validate that all required tags are present and correctly formatted"""
    # Check required tags
    for key, description in REQUIRED_TAGS.items():
        if key not in tags:
            return False, f"Missing required tag '{key}': {description}"
        if not tags[key] or not tags[key].strip():
            return False, f"Required tag '{key}' cannot be empty. {description}"
    
    # Validate tag key format
    for key in tags.keys():
        for prefix in RESERVED_PREFIXES:
            if key.startswith(prefix):
                return False, f"Tag key '{key}' uses reserved prefix '{prefix}'"
        if not TAG_KEY_PATTERN.match(key):
            return False, f"Tag key '{key}' is invalid. Must be lowercase alphanumeric characters and hyphens only"
    
    # Validate tag value length
    for key, value in tags.items():
        if len(value) > TAG_VALUE_MAX_LENGTH:
            return False, f"Tag value for '{key}' exceeds maximum length of {TAG_VALUE_MAX_LENGTH} characters"
    
    # Additional validation for production
    if environment == "production":
        if 'cost-center' not in tags and not tags.get('project-code'):
            return False, "Production deployments should have either 'cost-center' or 'project-code' tag for cost tracking"
    
    return True, None
