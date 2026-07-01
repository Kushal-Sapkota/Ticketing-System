from pydantic import BaseModel

from app.models.enums import AvailabilityStatus, PriorityLevel
from app.schemas.agent import AgentAvailabilitySummary


class AgentTicketCount(BaseModel):
    id: int
    full_name: str
    availability: AvailabilityStatus
    role: str
    ticket_count: int


class PriorityCount(BaseModel):
    priority: PriorityLevel
    count: int


class DashboardSummary(BaseModel):
    open_tickets: int
    tickets_per_agent: list[AgentTicketCount]
    tickets_by_priority: list[PriorityCount]
    agent_availability: list[AgentAvailabilitySummary]
