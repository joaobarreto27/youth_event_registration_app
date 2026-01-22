from fastapi import FastAPI
from .engine_database.database import engine, create_schema
from .routes.routes_events import router_events

engine = engine
create_schema = create_schema

app = FastAPI(
    title="Youth Event Registration API",
    description="Sistema de cadastro de eventos e registro de participantes",
    version="1.0.0",
)
app.include_router(router_events, prefix="/eventos", tags=["eventos"])
