from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from ..engine_database.database import SessionLocal, get_db
from ..validator.EventValidatorSchema import (
    ValidatorEventCreate,
    ValidatorEventResponse,
    ValidatorEventUpdate,
)
from ..validator.ParticipantValidatorSchema import (
    ValidatorParticipantCreate,
    ValidatorParticipantResponse,
    ValidatorParticipantUpdate,
)
from ..validator.RegisteredEventValidatorSchema import (
    ValidatorRegisteredEventCreate,
    ValidatorRegisteredEventResponse,
)
from ..crud.create_crud import (
    create_event,
    get_all_events,
    get_all_unique_participants,
    get_event_by_id,
    update_event,
    delete_event,
    register_participant,
    get_event_participants,
    get_participant_by_id,
    update_participant,
    delete_participant,
    register_event_creation,
    get_registered_events,
    get_registered_event_by_id,
    delete_registered_event,
)
from typing import Dict, List

router_events = APIRouter()

# ==================== EVENTS ENDPOINTS ====================


# Rota para listar todos os eventos
@router_events.get("/", response_model=list[ValidatorEventResponse])
async def get_all_events_endpoint(db: Session = Depends(get_db)):
    """Get all registered events"""
    return await get_all_events(db)


@router_events.get("/participants/unique", response_model=List[Dict[str, str]])
async def get_unique_participants(db: Session = Depends(get_db)):
    """
    Retorna todos os participantes únicos (nomes distintos) de todos os eventos.
    Otimizado para evitar N+1 queries.
    """
    return await get_all_unique_participants(db)


# Rota para criar novo evento
@router_events.post("/", response_model=ValidatorEventResponse)
async def create_event_endpoint(
    event: ValidatorEventCreate, db: Session = Depends(get_db)
):
    """Create a new event"""
    return await create_event(db, event)


# Rota para obter evento específico
@router_events.get("/{event_id}", response_model=ValidatorEventResponse)
async def get_event_by_id_endpoint(
    event_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    """Get a specific event by ID"""
    return await get_event_by_id(db, event_id)


# Rota para atualizar evento
@router_events.put("/{event_id}", response_model=ValidatorEventResponse)
async def update_event_endpoint(
    event_id: int = Path(..., gt=0),
    event_update: ValidatorEventUpdate = None,
    db: Session = Depends(get_db),
):
    """Update an event"""
    return await update_event(db, event_id, event_update)


# Rota para deletar evento
@router_events.delete("/{event_id}")
async def delete_event_endpoint(
    event_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    """Delete an event"""
    return await delete_event(db, event_id)


# ==================== PARTICIPANTS ENDPOINTS ====================


# Registrar participante em um evento
@router_events.post(
    "/{event_id}/participants", response_model=ValidatorParticipantResponse
)
async def register_participant_endpoint(
    event_id: int = Path(..., gt=0),
    participant: ValidatorParticipantCreate = None,
    db: Session = Depends(get_db),
):
    return await register_participant(db, event_id, participant)


# Listar participantes de um evento específico
@router_events.get(
    "/{event_id}/participants", response_model=list[ValidatorParticipantResponse]
)
async def get_event_participants_endpoint(
    event_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return await get_event_participants(db, event_id)


# Detalhes, atualização e deleção de participantes por ID global
@router_events.get(
    "/participants/{registration_id}", response_model=ValidatorParticipantResponse
)
async def get_participant_by_id_endpoint(
    registration_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return await get_participant_by_id(db, registration_id)


@router_events.put(
    "/participants/{registration_id}", response_model=ValidatorParticipantResponse
)
async def update_participant_endpoint(
    registration_id: int = Path(..., gt=0),
    participant_update: ValidatorParticipantUpdate = None,
    db: Session = Depends(get_db),
):
    return await update_participant(db, registration_id, participant_update)


@router_events.delete("/participants/{registration_id}")
async def delete_participant_endpoint(
    registration_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return await delete_participant(db, registration_id)


# ==================== REGISTERED EVENTS ENDPOINTS ====================


# Rota para registrar criação de um evento
@router_events.post("/registered/", response_model=ValidatorRegisteredEventResponse)
async def register_event_creation_endpoint(
    event_id: int,
    event_name: str,
    created_by: str,
    db: Session = Depends(get_db),
):
    """Register a created event in the registered_events table"""
    return await register_event_creation(db, event_id, event_name, created_by)


# Rota para listar eventos registrados (criados)
@router_events.get(
    "/registered/", response_model=list[ValidatorRegisteredEventResponse]
)
async def get_registered_events_endpoint(db: Session = Depends(get_db)):
    """Get all registered (created) events"""
    return await get_registered_events(db)


# Rota para obter um evento registrado específico
@router_events.get(
    "/registered/{registered_event_id}", response_model=ValidatorRegisteredEventResponse
)
async def get_registered_event_by_id_endpoint(
    registered_event_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    """Get a specific registered event by ID"""
    return await get_registered_event_by_id(db, registered_event_id)


# Rota para deletar um evento registrado
@router_events.delete("/registered/{registered_event_id}")
async def delete_registered_event_endpoint(
    registered_event_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    """Delete a registered event"""
    return await delete_registered_event(db, registered_event_id)
