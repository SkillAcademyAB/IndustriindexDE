"""
DuckDB Repository for local database operations.
"""

import duckdb
from pathlib import Path
from typing import Any, List, Optional


class DuckDBRepository:
    """
    Repository class for DuckDB database operations.
    Provides a connection to a local DuckDB database file.
    """

    def __init__(self, db_path: str = "data/industriindex.duckdb"):
        """
        Initialize the DuckDB repository.

        Args:
            db_path: Path to the DuckDB database file. Defaults to
                'data/industriindex.duckdb'
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[duckdb.DuckDBPyConnection] = None

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Get or create a connection to the DuckDB database.

        Returns:
            DuckDB connection object
        """
        if self._connection is None:
            self._connection = duckdb.connect(str(self.db_path))
        return self._connection

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Query results
        """
        conn = self.get_connection()
        if params:
            return conn.execute(query, params).fetchall()
        return conn.execute(query).fetchall()

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query string
            params_list: List of parameter tuples
        """
        conn = self.get_connection()
        conn.executemany(query, params_list)

    def create_table_from_dataframe(
        self, df: Any, table_name: str, if_exists: str = "replace"
    ) -> None:
        """
        Create a table from a pandas DataFrame.

        Args:
            df: Pandas DataFrame
            table_name: Name of the table to create
            if_exists: Action if table exists ('replace', 'append', 'fail')
        """
        conn = self.get_connection()
        # Register the DataFrame as a DuckDB view for SQL access
        conn.register("df", df)
        # Check if the table exists
        table_exists = conn.execute(
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        ).fetchone()[0] > 0
        if if_exists == "replace":
            if table_exists:
                conn.execute(f"DROP TABLE {table_name}")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        elif if_exists == "fail":
            if table_exists:
                raise ValueError(f"Table '{table_name}' already exists.")
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        elif if_exists == "append":
            if table_exists:
                # Insert rows from df into the existing table
                conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            else:
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        else:
            raise ValueError(f"Invalid value for if_exists: {if_exists}")
    def query_to_dataframe(self, query: str) -> Any:
        """
        Execute a query and return results as a pandas DataFrame.

        Args:
            query: SQL query string

        Returns:
            Pandas DataFrame with query results
        """
        conn = self.get_connection()
        return conn.execute(query).df()

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
