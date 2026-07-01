import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import IssueType, PriorityLevel, TicketStatus, TicketEventAction


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    requester_contact: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    issue_type: Mapped[IssueType] = mapped_column(
        sa.Enum(
            IssueType,
            name="issue_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    priority: Mapped[PriorityLevel] = mapped_column(
        sa.Enum(
            PriorityLevel,
            name="priority_level",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=PriorityLevel.medium,
    )
    status: Mapped[TicketStatus] = mapped_column(
        sa.Enum(
            TicketStatus,
            name="ticket_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=TicketStatus.open,
    )
    asset_id: Mapped[int | None] = mapped_column(sa.Integer, nullable=True, index=True)
    assigned_agent_id: Mapped[int | None] = mapped_column(sa.ForeignKey("agents.id"), nullable=True, index=True)
    created_by_agent_id: Mapped[int] = mapped_column(sa.ForeignKey("agents.id"), nullable=False, index=True)
    updated_by_agent_id: Mapped[int | None] = mapped_column(sa.ForeignKey("agents.id"), nullable=True, index=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False
    )

    assigned_agent = relationship("Agent", foreign_keys=[assigned_agent_id])
    created_by_agent = relationship("Agent", foreign_keys=[created_by_agent_id])
    updated_by_agent = relationship("Agent", foreign_keys=[updated_by_agent_id])
    history = relationship(
        "TicketEvent", cascade="all, delete-orphan", order_by="TicketEvent.created_at", back_populates="ticket"
    )


class TicketEvent(Base):
    __tablename__ = "ticket_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("tickets.id"), nullable=False, index=True)
    actor_agent_id: Mapped[int | None] = mapped_column(sa.ForeignKey("agents.id"), nullable=True, index=True)
    action: Mapped[TicketEventAction] = mapped_column(
        sa.Enum(
            TicketEventAction,
            name="ticket_event_action",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    field_name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    new_value: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    ticket = relationship("Ticket", back_populates="history")
    actor = relationship("Agent")
