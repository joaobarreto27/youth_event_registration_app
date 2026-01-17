from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ValidatorRegisteredEventCreate(BaseModel):
    id_event: int
    event_name: str
    created_by: str


class ValidatorRegisteredEventResponse(BaseModel):
    id_registered_event: int
    id_event: int
    event_name: str
    created_by: str
    created_date: datetime

    class Config:
        from_attributes = True


class ValidatorRegisteredEventUpdate(BaseModel):
    event_name: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True
