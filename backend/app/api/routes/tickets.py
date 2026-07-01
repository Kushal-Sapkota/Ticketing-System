from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_agent
from app.db.session import get_db
from app.models.agent import Agent
from app.models.enums import AvailabilityStatus, PriorityLevel, TicketEventAction, TicketStatus
from app.models.ticket import Ticket, TicketEvent
from app.schemas.ticket import (
    TicketAssignmentResponse,
    TicketAssignmentUpdate,
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketStatusUpdate,
)
from app.services.notification import notification_service


router = APIRouter(prefix="/tickets", tags=["tickets"])


def _load_ticket_detail(db: Session, ticket_id: UUID) -> Ticket | None:
    return (
        db.query(Ticket)
        .options(
            joinedload(Ticket.assigned_agent),
            joinedload(Ticket.created_by_agent),
            joinedload(Ticket.updated_by_agent),
            joinedload(Ticket.history).joinedload(TicketEvent.actor),
        )
        .filter(Ticket.id == ticket_id)
        .one_or_none()
    )


@router.get("", response_model=list[TicketListItem])
def list_tickets(
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    priority: PriorityLevel | None = None,
    assigned_agent_id: int | None = None,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> list[TicketListItem]:
    query = db.query(Ticket).options(joinedload(Ticket.assigned_agent)).order_by(Ticket.created_at.desc())
    if status_filter is not None:
        query = query.filter(Ticket.status == status_filter)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assigned_agent_id is not None:
        query = query.filter(Ticket.assigned_agent_id == assigned_agent_id)
    return query.all()


@router.post("", response_model=TicketDetail, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> TicketDetail:
    ticket = Ticket(
        requester_name=payload.requester_name.strip(),
        requester_contact=payload.requester_contact.strip(),
        issue_type=payload.issue_type,
        description=payload.description.strip(),
        priority=payload.priority,
        status=payload.status,
        asset_id=payload.asset_id,
        created_by_agent_id=current_agent.id,
        updated_by_agent_id=current_agent.id,
    )
    db.add(ticket)
    db.flush()
    db.add(
        TicketEvent(
            ticket_id=ticket.id,
            actor_agent_id=current_agent.id,
            action=TicketEventAction.created,
            field_name="ticket",
            old_value=None,
            new_value=ticket.status.value,
            note="Ticket created manually by an agent",
        )
    )
    db.commit()
    loaded = _load_ticket_detail(db, ticket.id)
    if loaded is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ticket reload failed")
    return loaded  # type: ignore[return-value]


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> TicketDetail:
    ticket = _load_ticket_detail(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketDetail)
def update_ticket_status(
    ticket_id: UUID,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> TicketDetail:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if ticket.status == payload.status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already has that status")

    old_status = ticket.status.value
    ticket.status = payload.status
    ticket.updated_by_agent_id = current_agent.id
    db.add(ticket)
    db.add(
        TicketEvent(
            ticket_id=ticket.id,
            actor_agent_id=current_agent.id,
            action=TicketEventAction.status_changed,
            field_name="status",
            old_value=old_status,
            new_value=payload.status.value,
            note=f"Status changed by {current_agent.full_name}",
        )
    )
    db.commit()
    loaded = _load_ticket_detail(db, ticket.id)
    if loaded is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ticket reload failed")
    return loaded  # type: ignore[return-value]


@router.patch("/{ticket_id}/assignment", response_model=TicketAssignmentResponse)
def assign_ticket(
    ticket_id: UUID,
    payload: TicketAssignmentUpdate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> TicketAssignmentResponse:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    assignee = db.get(Agent, payload.assigned_agent_id)
    if assignee is None or not assignee.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned agent is not available")
    if assignee.availability != AvailabilityStatus.available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned agent must be available")
    if ticket.assigned_agent_id == assignee.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already assigned to that agent")

    old_agent_id = ticket.assigned_agent_id
    ticket.assigned_agent_id = assignee.id
    ticket.updated_by_agent_id = current_agent.id
    db.add(ticket)
    db.add(
        TicketEvent(
            ticket_id=ticket.id,
            actor_agent_id=current_agent.id,
            action=TicketEventAction.assigned,
            field_name="assigned_agent_id",
            old_value=str(old_agent_id) if old_agent_id is not None else None,
            new_value=str(assignee.id),
            note=f"Assigned to {assignee.full_name} by {current_agent.full_name}",
        )
    )
    db.commit()
    loaded = _load_ticket_detail(db, ticket.id)
    if loaded is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ticket reload failed")
    notification_message = notification_service.publish_assignment(
        {
            "ticket_id": str(ticket.id),
            "ticket_status": ticket.status.value,
            "assigned_agent_id": assignee.id,
            "assigned_agent_name": assignee.full_name,
            "assigned_by": current_agent.full_name,
            "notification_type": "ticket.assignment",
        }
    )
    return TicketAssignmentResponse(ticket=loaded, notification=notification_message)
