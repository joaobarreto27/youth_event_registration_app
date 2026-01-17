from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from . import Base


class Events(Base):
    __tablename__ = "events"

    id_event = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(255), unique=True, nullable=False)
    create_date = Column(DateTime(timezone=True), default=func.now(), index=True)
    update_date = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), index=True
    )
