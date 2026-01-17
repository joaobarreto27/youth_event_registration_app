from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from . import Base


class RegisteredEvent(Base):
    __tablename__ = "registered_events"

    id_registered_event = Column(Integer, primary_key=True, index=True)
    id_event = Column(
        Integer, ForeignKey("events.id_event"), nullable=False, index=True
    )
    event_name = Column(String(255), nullable=False)
    created_by = Column(String(255), nullable=False)
    created_date = Column(DateTime(timezone=True), default=func.now(), index=True)

    # Constraint para garantir que cada evento é criado apenas uma vez
    __table_args__ = (UniqueConstraint("id_event", name="uq_registered_event"),)
