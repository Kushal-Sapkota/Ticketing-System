from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.models.enums import AgentRole
from app.core.security import extract_subject
from app.db.session import get_db
from app.models.agent import Agent


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_agent(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Agent:
    try:
        subject, _role = extract_subject(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials") from exc

    agent = db.get(Agent, int(subject))
    if agent is None or not agent.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing agent")
    return agent


def get_current_admin(current_agent: Agent = Depends(get_current_agent)) -> Agent:
    if current_agent.role != AgentRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_agent
