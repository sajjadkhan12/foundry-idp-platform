"""Business Unit context helpers for multi-tenancy support"""
import uuid
from typing import Union

def get_business_unit_domain_by_uuid(bu_id: Union[str, uuid.UUID]) -> str:
    """
    Get the domain string from business unit ID.
    Used for Casbin enforcement contexts.
    
    Args:
        bu_id: Business Unit UUID (string or UUID object)
        
    Returns:
        str: Domain string (currently just the UUID)
    """
    return str(bu_id)
