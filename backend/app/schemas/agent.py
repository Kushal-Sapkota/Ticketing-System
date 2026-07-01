from pydantic import BaseModel

from app.models.enums import AvailabilityStatus, AgentRole


class AgentListItem(BaseModel):
    id: int
    email: str
    full_name: str
    role: AgentRole
    availability: AvailabilityStatus
    is_active: bool

    model_config = {"from_attributes": True}


class AvailabilityUpdate(BaseModel):
    availability: AvailabilityStatus


class AgentAvailabilitySummary(BaseModel):
    id: int
    full_name: str
    availability: AvailabilityStatus
    role: AgentRole

    model_config = {"from_attributes": True}
