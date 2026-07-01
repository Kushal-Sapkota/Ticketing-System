from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_agent
from app.db.session import get_db
from app.models.agent import Agent
from app.models.enums import AvailabilityStatus
from app.schemas.agent import AgentAvailabilitySummary, AgentListItem, AvailabilityUpdate


router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentListItem])
def list_agents(
    availability: AvailabilityStatus | None = None,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> list[AgentListItem]:
    query = db.query(Agent)
    if availability:
        query = query.filter(Agent.availability == availability)
    agents = query.order_by(Agent.full_name.asc()).all()
    return agents


@router.get("/available", response_model=list[AgentListItem])
def list_available_agents(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> list[AgentListItem]:
    return db.query(Agent).filter(Agent.availability == AvailabilityStatus.available).order_by(Agent.full_name.asc()).all()


@router.patch("/me/availability", response_model=AgentListItem)
def update_own_availability(
    payload: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> AgentListItem:
    current_agent.availability = payload.availability
    db.add(current_agent)
    db.commit()
    db.refresh(current_agent)
    return current_agent


@router.get("/availability", response_model=list[AgentAvailabilitySummary])
def list_agent_availability(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent),
) -> list[AgentAvailabilitySummary]:
    return db.query(Agent).order_by(Agent.full_name.asc()).all()
