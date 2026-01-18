from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time
import os
from typing import Optional
from dotenv import load_dotenv


class ConnectionDatabase:
    def __init__(
        self,
        base: Optional[object] = None,
        sgdb_name: str = "postgresql",
    ) -> None:
        self.base = base
        self.sgdb_name = sgdb_name
        self.engine = None

        load_dotenv()

    def initialize_engine(self):
        if self.sgdb_name != "postgresql":
            raise ValueError(f"SGBD não suportado: {self.sgdb_name}")

        # Pega as variáveis do ambiente (carregadas do .env)
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        # Validação básica
        if not all([db_user, db_pass, db_name]):
            raise ValueError(
                "Faltam variáveis obrigatórias no .env: "
                "DB_USER, DB_PASSWORD e DB_NAME são requeridos"
            )

        connection_string = (
            f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )

        return create_engine(connection_string)

    def connect(self, max_retries: int = 5, wait_seconds: int = 2):
        for attempt in range(1, max_retries + 1):
            try:
                self.engine = self.initialize_engine()

                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print("Conexão com o banco de dados estabelecida com sucesso!")
                return self.engine

            except OperationalError as e:
                print(f"Tentativa {attempt}/{max_retries} falhou: {e}")
                if attempt == max_retries:
                    raise Exception(
                        "Não foi possível conectar ao banco após várias tentativas"
                    )
                time.sleep(wait_seconds)

    def create_schema(self, max_retries: int = 5, wait_seconds: int = 2):
        if self.base is None:
            raise ValueError("Modelo base (declarative_base) não foi fornecido")
        if self.engine is None:
            self.connect()  # Garante que o engine existe

        for attempt in range(1, max_retries + 1):
            try:
                self.base.metadata.create_all(bind=self.engine)  # pyright: ignore[reportAttributeAccessIssue]
                print("Esquema criado com sucesso!")
                return
            except OperationalError as e:
                print(f"Tentativa {attempt}/{max_retries} falhou ao criar schema: {e}")
                if attempt == max_retries:
                    raise
                time.sleep(wait_seconds)
