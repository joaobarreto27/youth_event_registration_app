from sqlalchemy import create_engine, text
from dotenv import dotenv_values
from sqlalchemy.exc import OperationalError
import time
from pathlib import Path
from typing import Optional


class ConnectionDatabase:
    def __init__(
        self,
        base: Optional[object] = None,
        connection_folder: str = "db_connection",
        sgdb_name: str = "postgresql",
        file_name: str = ".env.dev_youth_event_registration_app",
    ) -> None:
        self.base = base
        self.connection_folder = connection_folder
        self.sgbd_name = sgdb_name
        self.file_name = file_name
        self.current_dir = None
        self.path_connection = None
        self.engine = None

    def initialize_engine(self):
        self.current_dir = Path(__file__).resolve().parent
        self.path_connection = self.current_dir.parent.joinpath(
            self.connection_folder, self.sgbd_name, self.file_name
        )

        if self.sgbd_name == "postgresql":
            if not self.path_connection.is_file():
                raise FileNotFoundError(
                    f"Configuration file '{self.path_connection}' not found."
                )

            env_vars = dotenv_values(dotenv_path=self.path_connection)

            settings = {
                "db_host": env_vars["DB_HOST"],
                "db_user": env_vars["DB_USER"],
                "db_pass": env_vars["DB_PASSWORD"],
                "db_name": env_vars["DB_NAME"],
                "db_port": env_vars["DB_PORT"],
            }

            connection_string = f"postgresql+psycopg2://{settings['db_user']}:{settings['db_pass']}@{settings['db_host']}:{settings['db_port']}/{settings['db_name']}"
            engine = create_engine(connection_string)
            return engine

        else:
            raise ValueError(f"SGBD '{self.sgbd_name}' not supported.")

    def connect(self, max_retries=5, wait_seconds=1):
        for number in range(1, max_retries + 1):
            try:
                self.engine = self.initialize_engine()

                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return self.engine
            except OperationalError as e:
                print("Failed to connect!")
                if number == max_retries:
                    print("Maximum number of save attempts reached.")

                else:
                    time.sleep(wait_seconds)

    def create_schema(self, max_retries=5, wait_seconds=1):
        for number in range(1, max_retries + 1):
            try:
                if self.base is not None and self.engine is not None:
                    self.base.metadata.create_all(bind=self.engine)  # type: ignore
                    return
            except OperationalError as e:
                print("Failed to create table!")
                if number == max_retries:
                    raise
                else:
                    time.sleep(wait_seconds)
