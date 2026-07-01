from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import IssueType, PriorityLevel, TicketStatus, TicketEventAction
from app.schemas.auth import AgentPublic


class TicketCreate(BaseModel):
    requester_name: str = Field(min_length=2, max_length=255)
    requester_contact: str = Field(min_length=3, max_length=255)
    issue_type: IssueType
    description: str = Field(min_length=5)
    priority: PriorityLevel = PriorityLevel.medium
    status: TicketStatus = TicketStatus.open
    asset_id: int | None = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssignmentUpdate(BaseModel):
    assigned_agent_id: int


class TicketEventOut(BaseModel):
    id: UUID
    action: TicketEventAction
    field_name: str | None
    old_value: str | None
    new_value: str | None
    note: str | None
    created_at: datetime
    actor: AgentPublic | None = None

    model_config = {"from_attributes": True}


class TicketListItem(BaseModel):
    id: UUID
    requester_name: str
    requester_contact: str
    issue_type: IssueType
    description: str
    priority: PriorityLevel
    status: TicketStatus
    asset_id: int | None
    created_at: datetime
    updated_at: datetime
    assigned_agent: AgentPublic | None = None

    model_config = {"from_attributes": True}


class TicketDetail(TicketListItem):
    created_by_agent: AgentPublic
    updated_by_agent: AgentPublic | None = None
    history: list[TicketEventOut] = Field(default_factory=list)


class TicketAssignmentResponse(BaseModel):
    ticket: TicketDetail
    notification: str
