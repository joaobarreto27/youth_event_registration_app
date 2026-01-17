from ..utils.ConnectionDatabaseSql import ConnectionDatabase
from ..schemas import Base
from ..schemas.SchemaEventParticipants import EventParticipant
from ..schemas.SchemaEvents import Events
from ..schemas.SchemaRegisteredEvents import RegisteredEvent
from sqlalchemy.orm import sessionmaker


def initialize_database():
    """
    Initialize the database connection and create tables if they do not exist.
    """
    connection = ConnectionDatabase(base=Base)
    engine = connection.connect()
    create_schema = connection.create_schema()
    return engine, create_schema


engine, create_schema = initialize_database()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency to get the database session.
    Yields a database session that can be used in CRUD operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
