"""
Tests for DuckDBRepository class.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.repositories import DuckDBRepository
import gc


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return str(tmp_path / "test_database.duckdb")


@pytest.fixture
def duckdb_repo(temp_db_path):
    """Create a DuckDBRepository instance with a temporary database."""
    repo = DuckDBRepository(temp_db_path)
    yield repo
    # Ensure the repository is closed before cleanup
    repo.close()
    # Force garbage collection to release file handles
    gc.collect()
    # Clean up the test database file
    db_file = Path(temp_db_path)
    if db_file.exists():
        try:
            db_file.unlink()
        except PermissionError:
            # If file is still locked, skip cleanup (tmp_path will clean it)
            pass


@pytest.fixture
def sample_dataframe():
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [100, 200, 300],
    })


class TestDuckDBRepositoryInitialization:
    """Test database initialization and connection management."""

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates parent directory if needed."""
        db_path = str(tmp_path / "nested" / "dir" / "test.duckdb")
        repo = DuckDBRepository(db_path)
        try:
            assert Path(db_path).parent.exists()
        finally:
            repo.close()

    def test_get_connection_creates_connection(self, duckdb_repo):
        """Test that get_connection creates a valid connection."""
        conn = duckdb_repo.get_connection()
        assert conn is not None

    def test_get_connection_returns_same_connection(self, duckdb_repo):
        """Test that get_connection returns the same connection on multiple calls."""
        conn1 = duckdb_repo.get_connection()
        conn2 = duckdb_repo.get_connection()
        assert conn1 is conn2

    def test_database_file_created(self, temp_db_path):
        """Test that the database file is created after connection."""
        repo = DuckDBRepository(temp_db_path)
        try:
            repo.get_connection()
            assert Path(temp_db_path).exists()
        finally:
            repo.close()


class TestDuckDBRepositorySQLQueries:
    """Test SQL query execution."""

    def test_execute_query_without_params(self, duckdb_repo):
        """Test executing a simple query without parameters."""
        duckdb_repo.execute_query(
            "CREATE TABLE test (id INTEGER, name VARCHAR)"
        )
        duckdb_repo.execute_query("INSERT INTO test VALUES (1, 'Alice')")

        result = duckdb_repo.execute_query("SELECT * FROM test")
        assert len(result) == 1
        assert result[0] == (1, "Alice")

    def test_execute_query_with_params(self, duckdb_repo):
        """Test executing a query with parameters."""
        duckdb_repo.execute_query(
            "CREATE TABLE test (id INTEGER, name VARCHAR)"
        )
        duckdb_repo.execute_query(
            "INSERT INTO test VALUES (?, ?)", (1, "Alice")
        )

        result = duckdb_repo.execute_query(
            "SELECT * FROM test WHERE id = ?", (1,)
        )
        assert len(result) == 1
        assert result[0] == (1, "Alice")

    def test_execute_query_returns_all_rows(self, duckdb_repo):
        """Test that execute_query returns all matching rows."""
        duckdb_repo.execute_query(
            "CREATE TABLE test (id INTEGER, name VARCHAR)"
        )
        duckdb_repo.execute_query("INSERT INTO test VALUES (1, 'Alice')")
        duckdb_repo.execute_query("INSERT INTO test VALUES (2, 'Bob')")
        duckdb_repo.execute_query("INSERT INTO test VALUES (3, 'Charlie')")

        result = duckdb_repo.execute_query("SELECT * FROM test ORDER BY id")
        assert len(result) == 3
        assert result[0] == (1, "Alice")
        assert result[1] == (2, "Bob")
        assert result[2] == (3, "Charlie")


class TestDuckDBRepositoryExecuteMany:
    """Test execute_many functionality."""

    def test_execute_many_inserts_multiple_rows(self, duckdb_repo):
        """Test execute_many inserts multiple rows correctly."""
        duckdb_repo.execute_query(
            "CREATE TABLE test (id INTEGER, name VARCHAR)"
        )

        params_list = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
        duckdb_repo.execute_many(
            "INSERT INTO test VALUES (?, ?)", params_list
        )

        result = duckdb_repo.execute_query("SELECT COUNT(*) FROM test")
        assert result[0][0] == 3

    def test_execute_many_with_empty_list_raises_error(self, duckdb_repo):
        """Test execute_many with empty parameter list raises an error."""
        import duckdb

        duckdb_repo.execute_query(
            "CREATE TABLE test (id INTEGER, name VARCHAR)"
        )

        with pytest.raises(duckdb.InvalidInputException):
            duckdb_repo.execute_many("INSERT INTO test VALUES (?, ?)", [])


class TestDuckDBRepositoryDataFrameIntegration:
    """Test DataFrame integration."""

    def test_create_table_from_dataframe(self, duckdb_repo, sample_dataframe):
        """Test creating a table from a pandas DataFrame."""
        duckdb_repo.create_table_from_dataframe(sample_dataframe, "test_table")

        result = duckdb_repo.execute_query(
            "SELECT * FROM test_table ORDER BY id"
        )
        assert len(result) == 3
        assert result[0] == (1, "Alice", 100)
        assert result[1] == (2, "Bob", 200)
        assert result[2] == (3, "Charlie", 300)

    def test_create_table_from_dataframe_replace(
        self, duckdb_repo, sample_dataframe
    ):
        """Test that if_exists='replace' drops and recreates the table."""
        duckdb_repo.create_table_from_dataframe(sample_dataframe, "test_table")

        new_df = pd.DataFrame({"id": [10], "name": ["New"], "value": [1000]})
        duckdb_repo.create_table_from_dataframe(
            new_df, "test_table", if_exists="replace"
        )

        result = duckdb_repo.execute_query("SELECT * FROM test_table")
        assert len(result) == 1
        assert result[0] == (10, "New", 1000)

    def test_query_to_dataframe(self, duckdb_repo, sample_dataframe):
        """Test query_to_dataframe returns a pandas DataFrame."""
        duckdb_repo.create_table_from_dataframe(sample_dataframe, "test_table")

        result_df = duckdb_repo.query_to_dataframe(
            "SELECT * FROM test_table ORDER BY id"
        )

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ["id", "name", "value"]
        assert result_df.iloc[0]["name"] == "Alice"

    def test_query_to_dataframe_with_filter(
        self, duckdb_repo, sample_dataframe
    ):
        """Test query_to_dataframe with a WHERE clause."""
        duckdb_repo.create_table_from_dataframe(sample_dataframe, "test_table")

        result_df = duckdb_repo.query_to_dataframe(
            "SELECT * FROM test_table WHERE value > 150"
        )

        assert len(result_df) == 2
        assert all(result_df["value"] > 150)


class TestDuckDBRepositoryContextManager:
    """Test context manager functionality."""

    def test_context_manager_creates_connection(self, temp_db_path):
        """Test using DuckDBRepository as context manager."""
        with DuckDBRepository(temp_db_path) as repo:
            repo.execute_query("CREATE TABLE test (id INTEGER)")
            repo.execute_query("INSERT INTO test VALUES (1)")
            result = repo.execute_query("SELECT * FROM test")
            assert len(result) == 1

    def test_context_manager_closes_connection(self, temp_db_path):
        """Test that context manager closes connection on exit."""
        repo = None
        with DuckDBRepository(temp_db_path) as r:
            repo = r
            repo.execute_query("CREATE TABLE test (id INTEGER)")

        assert repo._connection is None


class TestDuckDBRepositoryConnectionCleanup:
    """Test connection cleanup."""

    def test_close_closes_connection(self, temp_db_path):
        """Test that close() closes the connection."""
        repo = DuckDBRepository(temp_db_path)
        repo.get_connection()  # Create connection
        assert repo._connection is not None

        repo.close()
        assert repo._connection is None

    def test_close_can_be_called_multiple_times(self, temp_db_path):
        """Test that close() can be called multiple times safely."""
        repo = DuckDBRepository(temp_db_path)
        repo.get_connection()

        repo.close()
        repo.close()  # Should not raise an exception
        assert repo._connection is None

    def test_close_without_connection(self, temp_db_path):
        """Test that close() works even if no connection was created."""
        repo = DuckDBRepository(temp_db_path)
        repo.close()  # Should not raise an exception
        assert repo._connection is None
