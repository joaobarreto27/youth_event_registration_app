from pathlib import Path
import pandas as pd
from ..utils.ConnectionDatabaseSql import ConnectionDatabase
from sqlalchemy import text


class SqlReadFile:
    """
    Class to read SQL files and execute queries against a database.
    """

    def __init__(self, sql_file: str, engine, current_dir: Path) -> None:
        self.sql_file: str = sql_file
        self.engine = engine
        self.current_dir = current_dir
        self.query: str = ""
        self.path = None
        self.df = None
        self.columns = None

    def read_sql_file(self):
        self.path = self.current_dir.parent.joinpath(
            "sql", "query", f"{self.sql_file}.sql"
        )

        if not self.path.is_file():
            raise FileNotFoundError(f"SQL file '{self.path}' not found.")

        with open(self.path, "r") as file:
            self.query = file.read()

        return self.query

    def execute_query_sql(self, params: dict = None):
        """
        Execute the SQL query and return the result as a DataFrame.
        """
        if not self.query:
            raise ValueError("Query is empty. Please read the SQL file first.")

        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(self.query), params or {})
                if result.returns_rows:
                    self.data = result.fetchall()
                    self.columns = result.keys()
                    return self.data
                else:
                    # Quando for um INSERT, UPDATE, etc.
                    return {"rowcount": result.rowcount}
            except Exception as e:
                raise RuntimeError(f"Error executing query: {e}")

    def query_to_dataframe(self):
        """
        Convert the SQL query result to a pandas DataFrame.
        """
        if not self.data:
            raise ValueError("Data is empty. Please execute the query first.")
        if not self.columns:
            raise ValueError("Columns are missing. Please execute the query first.")

        self.df = pd.DataFrame(self.data, columns=self.columns)
        return self.df
