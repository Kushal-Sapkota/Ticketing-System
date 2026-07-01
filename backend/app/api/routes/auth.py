from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_agent
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    agent = db.query(Agent).filter(Agent.email == payload.email.lower()).one_or_none()
    if agent is None or not verify_password(payload.password, agent.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=str(agent.id), role=agent.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_agent: Agent = Depends(get_current_agent)) -> MeResponse:
    return current_agent
