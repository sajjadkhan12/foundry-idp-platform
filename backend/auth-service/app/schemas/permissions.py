from pydantic import BaseModel
from typing import Optional

class PermissionCheckRequest(BaseModel):
    permission_slug: str
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None


class ServicePermissionCheckRequest(BaseModel):
    user_id: str
    permission_slug: str
    business_unit_id: Optional[str] = None
    organization_id: Optional[str] = None
