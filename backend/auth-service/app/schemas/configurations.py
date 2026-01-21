from pydantic import BaseModel
from typing import Optional

class SetConfigurationRequest(BaseModel):
    config_key: str
    config_value: str
    business_unit_id: Optional[str] = None
