from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.core.deps import get_current_agent
from app.db.session import get_db
from app.models.agent import Agent
from app.models.enums import TicketStatus
from app.models.ticket import Ticket
from app.schemas.dashboard import AgentTicketCount, DashboardSummary, PriorityCount
from app.schemas.agent import AgentAvailabilitySummary


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> DashboardSummary:
    open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.open).scalar() or 0

    tickets_per_agent_rows = (
        db.query(
            Agent.id,
            Agent.full_name,
            Agent.availability,
            Agent.role,
            func.count(Ticket.id).label("ticket_count"),
        )
        .outerjoin(Ticket, Ticket.assigned_agent_id == Agent.id)
        .group_by(Agent.id)
        .order_by(Agent.full_name.asc())
        .all()
    )
    tickets_per_agent = [
        AgentTicketCount(
            id=row.id,
            full_name=row.full_name,
            availability=row.availability,
            role=row.role.value if hasattr(row.role, "value") else str(row.role),
            ticket_count=int(row.ticket_count),
        )
        for row in tickets_per_agent_rows
    ]

    priority_rows = (
        db.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .order_by(Ticket.priority.asc())
        .all()
    )
    tickets_by_priority = [PriorityCount(priority=row[0], count=int(row[1])) for row in priority_rows]

    agents = db.query(Agent).order_by(Agent.full_name.asc()).all()
    agent_availability = [AgentAvailabilitySummary.model_validate(agent) for agent in agents]

    return DashboardSummary(
        open_tickets=int(open_tickets),
        tickets_per_agent=tickets_per_agent,
        tickets_by_priority=tickets_by_priority,
        agent_availability=agent_availability,
    )
