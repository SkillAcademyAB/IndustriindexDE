"""
Document Database Repository using TinyDB.
TinyDB is a lightweight, document-oriented database written in pure Python.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from tinydb import TinyDB
from tinydb.table import Document, Table


class DocumentRepository:
    """
    Repository class for TinyDB document database operations.
    Provides a lightweight JSON-based document storage.
    """

    def __init__(self, db_path: str = "data/documents.json"):
        """
        Initialize the Document repository.

        Args:
            db_path: Path to the TinyDB JSON file. Defaults to
                'data/documents.json'
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db: Optional[TinyDB] = None

    def get_db(self) -> TinyDB:
        """
        Get or create a connection to the TinyDB database.

        Returns:
            TinyDB database instance
        """
        if self._db is None:
            self._db = TinyDB(str(self.db_path), indent=2)
        return self._db

    def get_table(self, table_name: str = "_default") -> Table:
        """
        Get a specific table from the database.

        Args:
            table_name: Name of the table. Defaults to '_default'

        Returns:
            TinyDB Table instance
        """
        db = self.get_db()
        return db.table(table_name)

    def insert(
        self, document: Dict[str, Any], table_name: str = "_default"
    ) -> int:
        """
        Insert a document into the database.

        Args:
            document: Dictionary representing the document
            table_name: Name of the table

        Returns:
            Document ID
        """
        table = self.get_table(table_name)
        return table.insert(document)

    def insert_multiple(
        self, documents: List[Dict[str, Any]], table_name: str = "_default"
    ) -> List[int]:
        """
        Insert multiple documents into the database.

        Args:
            documents: List of document dictionaries
            table_name: Name of the table

        Returns:
            List of document IDs
        """
        table = self.get_table(table_name)
        return table.insert_multiple(documents)

    def get_all(self, table_name: str = "_default") -> List[Document]:
        """
        Get all documents from a table.

        Args:
            table_name: Name of the table

        Returns:
            List of all documents
        """
        table = self.get_table(table_name)
        return table.all()

    def search(
        self, condition: Callable, table_name: str = "_default"
    ) -> List[Document]:
        """
        Search for documents matching a condition.

        Args:
            condition: Query condition (e.g., where('field') == 'value')
            table_name: Name of the table

        Returns:
            List of matching documents
        """
        table = self.get_table(table_name)
        return table.search(condition)

    def get_by_id(
        self, doc_id: int, table_name: str = "_default"
    ) -> Optional[Document]:
        """
        Get a document by its ID.

        Args:
            doc_id: Document ID
            table_name: Name of the table

        Returns:
            Document if found, None otherwise
        """
        table = self.get_table(table_name)
        return table.get(doc_id=doc_id)

    def update(
        self,
        fields: Dict[str, Any],
        condition: Callable,
        table_name: str = "_default",
    ) -> List[int]:
        """
        Update documents matching a condition.

        Args:
            fields: Dictionary of fields to update
            condition: Query condition
            table_name: Name of the table

        Returns:
            List of updated document IDs
        """
        table = self.get_table(table_name)
        return table.update(fields, condition)

    def upsert(
        self,
        document: Dict[str, Any],
        condition: Callable,
        table_name: str = "_default",
    ) -> List[int]:
        """
        Update or insert a document.

        Args:
            document: Document to upsert
            condition: Query condition for finding existing document
            table_name: Name of the table

        Returns:
            List of affected document IDs
        """
        table = self.get_table(table_name)
        return table.upsert(document, condition)

    def remove(
        self, condition: Callable, table_name: str = "_default"
    ) -> List[int]:
        """
        Remove documents matching a condition.

        Args:
            condition: Query condition
            table_name: Name of the table

        Returns:
            List of removed document IDs
        """
        table = self.get_table(table_name)
        return table.remove(condition)

    def remove_all(self, table_name: str = "_default") -> None:
        """
        Remove all documents from a table.

        Args:
            table_name: Name of the table
        """
        table = self.get_table(table_name)
        table.truncate()

    def count(
        self,
        condition: Optional[Callable] = None,
        table_name: str = "_default",
    ) -> int:
        """
        Count documents in a table.

        Args:
            condition: Optional query condition
            table_name: Name of the table

        Returns:
            Number of documents
        """
        table = self.get_table(table_name)
        if condition:
            return len(table.search(condition))
        return len(table)

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._db:
            self._db.close()
            self._db = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
