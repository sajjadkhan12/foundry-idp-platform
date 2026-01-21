from pydantic import BaseModel
from typing import Optional

class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class CreateOrganizationWithAdminRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    admin_email: str
    admin_username: str
    admin_password: str
    admin_full_name: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
