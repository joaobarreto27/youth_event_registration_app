from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from . import Base


class EventParticipant(Base):
    __tablename__ = "event_participants"

    id_registration = Column(Integer, primary_key=True, index=True)
    id_event = Column(
        Integer, ForeignKey("events.id_event"), nullable=False, index=True
    )
    participant_name = Column(String(255), nullable=False)
    registration_date = Column(DateTime(timezone=True), default=func.now(), index=True)

    # Constraint para garantir que cada pessoa se registra apenas uma vez por evento
    __table_args__ = (
        UniqueConstraint("id_event", "participant_name", name="uq_event_participant"),
    )
