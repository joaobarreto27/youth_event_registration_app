from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ValidatorParticipantBase(BaseModel):
    """Base validator for Event Participant data"""

    participant_name: str = Field(
        ..., min_length=1, max_length=255, description="Participant name"
    )


class ValidatorParticipantCreate(ValidatorParticipantBase):
    """Validator for registering a participant in an event"""

    pass


class ValidatorParticipantResponse(ValidatorParticipantBase):
    """Validator for participant response"""

    id_registration: int
    id_event: int
    registration_date: datetime

    class Config:
        from_attributes = True


class ValidatorParticipantUpdate(BaseModel):
    """Validator for updating a participant"""

    participant_name: Optional[str] = Field(None, min_length=1, max_length=255)

    class Config:
        from_attributes = True
