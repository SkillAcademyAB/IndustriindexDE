import pytest
from pathlib import Path
import pandas as pd
from source.repositories import DuckDBRepository
import gc


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return str(tmp_path / "test_industriindex.duckdb")


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
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [100, 200, 300],
        }
    )


class TestDuckDBRepositoryInitialization:
    """Test database initialization and connection management."""

    def test_init_creates_parent_directory(self, tmp_path):
        """Test that initialization creates parent directory if it doesn't exist."""
        nested_path = tmp_path / "nested" / "dir" / "test.duckdb"
        repo = DuckDBRepository(str(nested_path))

        assert nested_path.parent.exists()
        repo.close()

    def test_init_with_default_path(self):
        """Test initialization with default database path."""
        repo = DuckDBRepository()
        assert repo.db_path == Path("data/industriindex.duckdb")
        repo.close()

    def test_get_connection_returns_connection(self, duckdb_repo):
        """Test that get_connection returns a valid connection."""
        conn = duckdb_repo.get_connection()
        assert conn is not None

    def test_get_connection_returns_same_connection(self, duckdb_repo):
        """Test that get_connection returns the same connection on multiple calls."""
        conn1 = duckdb_repo.get_connection()
        conn2 = duckdb_repo.get_connection()
        assert conn1 is conn2

    def test_connection_is_none_initially(self, temp_db_path):
        """Test that _connection is None before first use."""
        repo = DuckDBRepository(temp_db_path)
        assert repo._connection is None
        repo.close()


class TestDuckDBRepositorySQLExecution:
    """Test SQL query execution functionality."""

    def test_execute_query_without_params(self, duckdb_repo):
        """Test executing a query without parameters."""
        result = duckdb_repo.execute_query("SELECT 1 AS value")
        assert result == [(1,)]

    def test_execute_query_with_params(self, duckdb_repo):
        """Test executing a query with parameters."""
        # Create a table for testing
        duckdb_repo.execute_query(
            "CREATE TABLE test_params (id INTEGER, name VARCHAR)"
        )
        duckdb_repo.execute_query(
            "INSERT INTO test_params VALUES (1, 'Alice'), (2, 'Bob')"
        )

        result = duckdb_repo.execute_query(
            "SELECT * FROM test_params WHERE id = ?", (1,)
        )
        assert len(result) == 1
        assert result[0] == (1, "Alice")

    def test_execute_query_with_multiple_params(self, duckdb_repo):
        """Test executing a query with multiple parameters."""
        duckdb_repo.execute_query(
            "CREATE TABLE test_multi (id INTEGER, name VARCHAR, value INTEGER)"
        )
        duckdb_repo.execute_query(
            "INSERT INTO test_multi VALUES (1, 'Alice', 100), (2, 'Bob', 200)"
        )

        result = duckdb_repo.execute_query(
            "SELECT * FROM test_multi WHERE id = ? AND value > ?", (1, 50)
        )
        assert len(result) == 1
        assert result[0] == (1, "Alice", 100)

    def test_execute_query_create_and_insert(self, duckdb_repo):
        """Test creating a table and inserting data."""
        duckdb_repo.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name VARCHAR)"
        )
        duckdb_repo.execute_query(
            "INSERT INTO test_table VALUES (1, 'Test')"
        )

        result = duckdb_repo.execute_query("SELECT * FROM test_table")
        assert len(result) == 1
        assert result[0] == (1, "Test")


class TestDuckDBRepositoryExecuteMany:
    """Test execute_many functionality."""

    def test_execute_many_basic(self, duckdb_repo):
        """Test executing multiple inserts with execute_many."""
        duckdb_repo.execute_query(
            "CREATE TABLE test_batch (id INTEGER, name VARCHAR)"
        )

        params_list = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
        duckdb_repo.execute_many(
            "INSERT INTO test_batch VALUES (?, ?)", params_list
        )

        result = duckdb_repo.execute_query(
            "SELECT * FROM test_batch ORDER BY id"
        )
        assert len(result) == 3
        assert result[0] == (1, "Alice")
        assert result[1] == (2, "Bob")
        assert result[2] == (3, "Charlie")

    def test_execute_many_empty_list_raises_error(self, duckdb_repo):
        """Test execute_many with empty parameter list raises error."""
        import duckdb

        duckdb_repo.execute_query(
            "CREATE TABLE test_empty (id INTEGER, name VARCHAR)"
        )

        # DuckDB requires a non-empty list for executemany
        with pytest.raises(duckdb.InvalidInputException):
            duckdb_repo.execute_many(
                "INSERT INTO test_empty VALUES (?, ?)", []
            )


class TestDuckDBRepositoryDataFrameIntegration:
    """Test DataFrame integration functionality."""

    def test_create_table_from_dataframe_replace(
        self, duckdb_repo, sample_dataframe
    ):
        """Test creating a table from DataFrame with replace mode."""
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        result = duckdb_repo.execute_query(
            "SELECT * FROM test_df ORDER BY id"
        )
        assert len(result) == 3
        assert result[0] == (1, "Alice", 100)

    def test_create_table_from_dataframe_replace_existing(
        self, duckdb_repo, sample_dataframe
    ):
        """Test replacing an existing table with DataFrame."""
        # Create initial table
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        # Replace with new data
        new_df = pd.DataFrame({"id": [10], "name": ["New"], "value": [1000]})
        duckdb_repo.create_table_from_dataframe(new_df, "test_df", "replace")

        result = duckdb_repo.execute_query("SELECT * FROM test_df")
        assert len(result) == 1
        assert result[0] == (10, "New", 1000)

    def test_create_table_from_dataframe_append(
        self, duckdb_repo, sample_dataframe
    ):
        """Test appending DataFrame to existing table."""
        # Create initial table
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        # Append new data
        new_df = pd.DataFrame(
            {"id": [4, 5], "name": ["Dave", "Eve"], "value": [400, 500]}
        )
        duckdb_repo.create_table_from_dataframe(new_df, "test_df", "append")

        result = duckdb_repo.execute_query(
            "SELECT COUNT(*) FROM test_df"
        )
        assert result[0][0] == 5

    def test_create_table_from_dataframe_append_new_table(
        self, duckdb_repo, sample_dataframe
    ):
        """Test append mode creates table if it doesn't exist."""
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "new_table", "append"
        )

        result = duckdb_repo.execute_query("SELECT COUNT(*) FROM new_table")
        assert result[0][0] == 3

    def test_create_table_from_dataframe_fail_on_existing(
        self, duckdb_repo, sample_dataframe
    ):
        """Test fail mode raises error if table exists."""
        # Create table first
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        # Attempt to create again with fail mode
        with pytest.raises(ValueError, match="already exists"):
            duckdb_repo.create_table_from_dataframe(
                sample_dataframe, "test_df", "fail"
            )

    def test_create_table_from_dataframe_fail_new_table(
        self, duckdb_repo, sample_dataframe
    ):
        """Test fail mode creates table if it doesn't exist."""
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "new_table", "fail"
        )

        result = duckdb_repo.execute_query("SELECT COUNT(*) FROM new_table")
        assert result[0][0] == 3

    def test_create_table_from_dataframe_invalid_mode(
        self, duckdb_repo, sample_dataframe
    ):
        """Test invalid if_exists mode raises error."""
        with pytest.raises(ValueError, match="Invalid value for if_exists"):
            duckdb_repo.create_table_from_dataframe(
                sample_dataframe, "test_df", "invalid_mode"
            )

    def test_query_to_dataframe(self, duckdb_repo, sample_dataframe):
        """Test querying data and returning as DataFrame."""
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        result_df = duckdb_repo.query_to_dataframe(
            "SELECT * FROM test_df ORDER BY id"
        )

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ["id", "name", "value"]
        assert result_df.iloc[0]["name"] == "Alice"

    def test_query_to_dataframe_with_aggregation(
        self, duckdb_repo, sample_dataframe
    ):
        """Test querying with aggregation returns correct DataFrame."""
        duckdb_repo.create_table_from_dataframe(
            sample_dataframe, "test_df", "replace"
        )

        result_df = duckdb_repo.query_to_dataframe(
            "SELECT SUM(value) AS total FROM test_df"
        )

        assert result_df.iloc[0]["total"] == 600


class TestDuckDBRepositoryContextManager:
    """Test context manager functionality."""

    def test_context_manager_basic(self, temp_db_path):
        """Test using DuckDBRepository as context manager."""
        with DuckDBRepository(temp_db_path) as repo:
            result = repo.execute_query("SELECT 1 AS value")
            assert result == [(1,)]

    def test_context_manager_closes_connection(self, temp_db_path):
        """Test that context manager closes connection on exit."""
        repo = DuckDBRepository(temp_db_path)
        with repo:
            # Force connection creation
            repo.get_connection()
            assert repo._connection is not None

        # After exiting context, connection should be closed
        assert repo._connection is None

    def test_context_manager_with_operations(self, temp_db_path):
        """Test context manager with multiple operations."""
        with DuckDBRepository(temp_db_path) as repo:
            repo.execute_query(
                "CREATE TABLE test_ctx (id INTEGER, name VARCHAR)"
            )
            repo.execute_query(
                "INSERT INTO test_ctx VALUES (1, 'Test')"
            )
            result = repo.execute_query("SELECT * FROM test_ctx")
            assert result == [(1, "Test")]


class TestDuckDBRepositoryConnectionCleanup:
    """Test connection cleanup functionality."""

    def test_close_closes_connection(self, temp_db_path):
        """Test that close() properly closes the connection."""
        repo = DuckDBRepository(temp_db_path)
        repo.get_connection()
        assert repo._connection is not None

        repo.close()
        assert repo._connection is None

    def test_close_when_no_connection(self, temp_db_path):
        """Test that close() handles case when no connection exists."""
        repo = DuckDBRepository(temp_db_path)
        assert repo._connection is None

        # Should not raise an error
        repo.close()
        assert repo._connection is None

    def test_multiple_close_calls(self, temp_db_path):
        """Test that multiple close() calls don't raise errors."""
        repo = DuckDBRepository(temp_db_path)
        repo.get_connection()

        repo.close()
        repo.close()  # Should not raise
        assert repo._connection is None

    def test_reconnect_after_close(self, temp_db_path):
        """Test that connection can be re-established after close."""
        repo = DuckDBRepository(temp_db_path)

        # First connection
        repo.execute_query(
            "CREATE TABLE test_reconnect (id INTEGER)"
        )
        repo.close()

        # Reconnect
        result = repo.execute_query(
            "SELECT COUNT(*) FROM test_reconnect"
        )
        assert result[0][0] == 0
        repo.close()
