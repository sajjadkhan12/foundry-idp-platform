from pydantic import BaseModel
from typing import Optional, List

class CreateBusinessUnitRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    organization_id: Optional[str] = None


class UpdateBusinessUnitRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AddBusinessUnitMemberRequest(BaseModel):
    user_email: str
    role_ids: Optional[List[str]] = None


class CreateBusinessUnitGroupRequest(BaseModel):
    business_unit_id: str
    name: str
    description: Optional[str] = None
    role_id: str


class UpdateBusinessUnitGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
