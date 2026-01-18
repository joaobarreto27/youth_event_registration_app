from sqlalchemy.orm import Session
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
from ..schemas.SchemaEvents import Events
from ..schemas.SchemaEventParticipants import EventParticipant
from ..schemas.SchemaRegisteredEvents import RegisteredEvent
from ..engine_database.database import get_db, engine
from ..utils.SqlReadFile import SqlReadFile
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy import text
from typing import Any, Dict, List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


# ==================== EVENT OPERATIONS ====================


async def create_event(
    db: Session, event: ValidatorEventCreate, commit: bool = True
) -> ValidatorEventResponse:
    """
    Create a new event in the database.
    """
    current_dir = Path(__file__).parent

    # Validação: event_name não pode estar vazio
    if not event.event_name or len(event.event_name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do evento não pode estar vazio",
        )

    sql_file = "create_event"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    create_event_query = sql_reader.read_sql_file()

    try:
        result = db.execute(
            text(create_event_query),
            {"event_name": event.event_name.strip()},
        )
        row = result.mappings().one()  # 👈 importante
        if commit:
            db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"❌ Já existe uma ideia com esse nome {event.event_name}, vote na sessão abaixo **(🗳️ Votar em Ideias de Eventos)**."
            ),
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar evento.",
        )

    return ValidatorEventResponse.model_validate(row)


async def get_event_by_id(db: Session, event_id: int) -> dict[str, Any]:
    """
    Get a specific event by ID.
    """
    sql_file = "get_event_by_id"
    current_dir = Path(__file__).parent
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    query = sql_reader.read_sql_file()

    row = db.execute(text(query), {"id_event": event_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    return ValidatorEventResponse.model_validate(dict(row._mapping)).model_dump()


async def get_all_events(db: Session) -> list[dict[str, Any]]:
    """
    Get all events from database.
    """
    sql_file = "get_all_events"
    current_dir = Path(__file__).parent
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)

    sql_reader.read_sql_file()
    rows = sql_reader.execute_query_sql()

    if not rows:
        raise HTTPException(status_code=404, detail="Não há eventos cadastrados!")

    return [ValidatorEventResponse.model_validate(row).model_dump() for row in rows]


async def update_event(
    db: Session, event_id: int, event_update: ValidatorEventUpdate, commit: bool = True
) -> ValidatorEventResponse:
    """
    Update an event in the database.
    """
    current_dir = Path(__file__).parent

    # Verificar se evento existe
    row = db.execute(
        text("SELECT id_event FROM events WHERE id_event = :id_event"),
        {"id_event": event_id},
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    sql_file = "update_event"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    update_event_query = sql_reader.read_sql_file()
    query = text(update_event_query)

    result = db.execute(
        query,
        {
            "id_event": event_id,
            "event_name": event_update.event_name,
        },
    )

    row = result.fetchone()
    if commit:
        db.commit()

    if not row:
        raise HTTPException(status_code=500, detail="Erro ao atualizar evento")

    return ValidatorEventResponse.model_validate(row)


async def delete_event(
    db: Session, event_id: int, commit: bool = True
) -> dict[str, Any]:
    """
    Delete an event from the database.
    """
    current_dir = Path(__file__).parent

    # Verificar se evento existe
    row = db.execute(
        text("SELECT id_event FROM events WHERE id_event = :id_event"),
        {"id_event": event_id},
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    sql_file = "delete_event"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    delete_event_query = sql_reader.read_sql_file()
    query = text(delete_event_query)

    result = db.execute(query, {"id_event": event_id})

    if commit:
        db.commit()

    return {"detail": f"Evento {event_id} deletado com sucesso"}


# ==================== PARTICIPANT OPERATIONS ====================


async def register_participant(
    db: Session,
    event_id: int,
    participant: ValidatorParticipantCreate,
    commit: bool = True,
) -> ValidatorParticipantResponse:
    """
    Register a participant in an event.
    Each person can register only once per event (enforced by unique constraint).
    """
    current_dir = Path(__file__).parent

    # Validação: event existe
    event_exists = db.execute(
        text("SELECT id_event FROM events WHERE id_event = :id_event"),
        {"id_event": event_id},
    ).fetchone()

    if not event_exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    # Validação: participant_name não pode estar vazio
    if (
        not participant.participant_name
        or len(participant.participant_name.strip()) == 0
    ):
        raise HTTPException(
            status_code=400, detail="Nome do participante não pode estar vazio"
        )

    # Validação: participant não está registrado no evento
    participant_exists = db.execute(
        text(
            "SELECT id_registration FROM event_participants WHERE id_event = :id_event AND participant_name = :participant_name"
        ),
        {
            "id_event": event_id,
            "participant_name": participant.participant_name.strip(),
        },
    ).fetchone()

    if participant_exists:
        raise HTTPException(
            status_code=409,
            detail=f"Participante '{participant.participant_name}' já está registrado neste evento!",
        )

    sql_file = "register_participant"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    register_query = sql_reader.read_sql_file()
    query = text(register_query)
    result = db.execute(
        query,
        {
            "id_event": event_id,
            "participant_name": participant.participant_name.strip(),
        },
    )
    row = result.fetchone()
    if commit:
        db.commit()

    if not row:
        raise HTTPException(status_code=500, detail="Erro ao registrar participante")

    return ValidatorParticipantResponse.model_validate(row)


async def get_event_participants(db: Session, event_id: int) -> list[dict[str, Any]]:
    """
    Get all participants registered in a specific event.
    """
    current_dir = Path(__file__).parent

    # Verificar se evento existe
    event_exists = db.execute(
        text("SELECT id_event FROM events WHERE id_event = :id_event"),
        {"id_event": event_id},
    ).fetchone()

    if not event_exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    sql_file = "get_event_participants"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    query = sql_reader.read_sql_file()

    rows = db.execute(text(query), {"id_event": event_id}).fetchall()
    if not rows:
        return []

    return [
        ValidatorParticipantResponse.model_validate(dict(row._mapping)).model_dump()
        for row in rows
    ]


async def get_participant_by_id(db: Session, registration_id: int) -> dict[str, Any]:
    """
    Get a specific participant registration by ID.
    """
    sql_file = "get_participant_by_id"
    current_dir = Path(__file__).parent
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    query = sql_reader.read_sql_file()

    row = db.execute(text(query), {"id_registration": registration_id}).fetchone()
    if not row:
        raise HTTPException(
            status_code=404, detail="Registro de participante não encontrado!"
        )

    return ValidatorParticipantResponse.model_validate(dict(row._mapping)).model_dump()


async def update_participant(
    db: Session,
    registration_id: int,
    participant_update: ValidatorParticipantUpdate,
    commit: bool = True,
) -> ValidatorParticipantResponse:
    """
    Update a participant registration.
    """
    current_dir = Path(__file__).parent

    # Verificar se registro existe
    row = db.execute(
        text(
            "SELECT id_registration FROM event_participants WHERE id_registration = :id_registration"
        ),
        {"id_registration": registration_id},
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404, detail="Registro de participante não encontrado!"
        )

    sql_file = "update_participant"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    update_query = sql_reader.read_sql_file()
    query = text(update_query)

    result = db.execute(
        query,
        {
            "id_registration": registration_id,
            "participant_name": participant_update.participant_name,
        },
    )

    row = result.fetchone()
    if commit:
        db.commit()

    if not row:
        raise HTTPException(status_code=500, detail="Erro ao atualizar participante")

    return ValidatorParticipantResponse.model_validate(row)


async def delete_participant(
    db: Session, registration_id: int, commit: bool = True
) -> dict[str, Any]:
    """
    Delete a participant registration from an event.
    """
    current_dir = Path(__file__).parent

    # Verificar se registro existe
    row = db.execute(
        text(
            "SELECT id_registration FROM event_participants WHERE id_registration = :id_registration"
        ),
        {"id_registration": registration_id},
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=404, detail="Registro de participante não encontrado!"
        )

    sql_file = "delete_participant"
    sql_reader = SqlReadFile(sql_file=sql_file, engine=engine, current_dir=current_dir)
    delete_query = sql_reader.read_sql_file()
    query = text(delete_query)

    db.execute(query, {"id_registration": registration_id})

    if commit:
        db.commit()

    return {"detail": f"Participante {registration_id} removido do evento com sucesso"}


# ==================== REGISTERED EVENT OPERATIONS ====================


async def register_event_creation(
    db: Session,
    event_id: int,
    event_name: str,
    created_by: str,
    commit: bool = True,
) -> ValidatorRegisteredEventResponse:
    """
    Register a created event in the registered_events table.
    Each event can only be registered once.
    """
    current_dir = Path(__file__).parent

    # Validação: event existe
    event_exists = db.execute(
        text("SELECT id_event FROM events WHERE id_event = :id_event"),
        {"id_event": event_id},
    ).fetchone()

    if not event_exists:
        raise HTTPException(status_code=404, detail="Evento não encontrado!")

    # Validação: evento já foi registrado
    event_registered = db.execute(
        text(
            "SELECT id_registered_event FROM registered_events WHERE id_event = :id_event"
        ),
        {"id_event": event_id},
    ).fetchone()

    if event_registered:
        raise HTTPException(
            status_code=409,
            detail=f"Evento '{event_name}' já foi registrado!",
        )

    # Inserir evento registrado
    db_registered_event = RegisteredEvent(
        id_event=event_id,
        event_name=event_name,
        created_by=created_by,
    )
    db.add(db_registered_event)
    if commit:
        db.commit()
        db.refresh(db_registered_event)

    return ValidatorRegisteredEventResponse.model_validate(db_registered_event)


async def get_registered_events(db: Session) -> list[dict[str, Any]]:
    """
    Get all registered events (created events, not voted events).
    """
    try:
        rows = db.query(RegisteredEvent).all()
        if not rows:
            return []
        return [
            ValidatorRegisteredEventResponse.model_validate(row).model_dump()
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar eventos registrados: {str(e)}"
        )


async def get_registered_event_by_id(
    db: Session, registered_event_id: int
) -> dict[str, Any]:
    """
    Get a specific registered event by ID.
    """
    row = (
        db.query(RegisteredEvent)
        .filter(RegisteredEvent.id_registered_event == registered_event_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Evento registrado não encontrado!")

    return ValidatorRegisteredEventResponse.model_validate(row).model_dump()


async def delete_registered_event(
    db: Session, registered_event_id: int, commit: bool = True
) -> dict[str, Any]:
    """
    Delete a registered event.
    """
    # Verificar se registro existe
    row = (
        db.query(RegisteredEvent)
        .filter(RegisteredEvent.id_registered_event == registered_event_id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Evento registrado não encontrado!")

    db.delete(row)
    if commit:
        db.commit()

    return {"detail": f"Evento registrado {registered_event_id} removido com sucesso"}


async def get_all_unique_participants(db: Session) -> List[Dict[str, str]]:
    """
    Retorna lista de participantes únicos (nomes distintos) em ordem alfabética.
    Muito mais eficiente que iterar por evento.
    """
    sql = text("""
        SELECT DISTINCT participant_name
        FROM event_participants
        WHERE participant_name IS NOT NULL AND participant_name != ''
        ORDER BY participant_name ASC
    """)

    try:
        result = db.execute(sql).fetchall()
        return [{"participant_name": row[0].strip()} for row in result if row[0]]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar participantes únicos: {str(e)}"
        )
