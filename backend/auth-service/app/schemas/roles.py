from pydantic import BaseModel
from typing import Optional, List

class CreateRoleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_platform_role: bool = False
    permissions: Optional[List[str]] = None


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_platform_role: Optional[bool] = None
    permissions: Optional[List[str]] = None


class AssignRoleRequest(BaseModel):
    role_name: str
    organization_id: Optional[str] = None
