import os
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.agent import Agent
from app.models.enums import AgentRole, AvailabilityStatus


def main() -> int:
    Base.metadata.create_all(bind=engine)
    email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@company.local").lower()
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")
    full_name = os.getenv("DEFAULT_ADMIN_NAME", "Default Admin")

    with SessionLocal() as db:
        existing = db.scalar(select(Agent).where(Agent.email == email))
        if existing is not None:
            print(f"Admin agent already exists: {email}")
            return 0

        admin = Agent(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=AgentRole.admin,
            availability=AvailabilityStatus.available,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created default admin agent: {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
