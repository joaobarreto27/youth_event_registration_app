from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ValidatorEventBase(BaseModel):
    """Base validator for Event data"""

    event_name: str = Field(..., min_length=1, max_length=255, description="Event name")


class ValidatorEventCreate(ValidatorEventBase):
    """Validator for creating a new event"""

    pass


class ValidatorEventResponse(ValidatorEventBase):
    """Validator for event response"""

    id_event: int
    create_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True


class ValidatorEventUpdate(BaseModel):
    """Validator for updating an event"""

    event_name: Optional[str] = Field(None, min_length=1, max_length=255)

    class Config:
        from_attributes = True
