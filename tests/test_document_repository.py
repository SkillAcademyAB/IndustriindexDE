import pytest
from pathlib import Path
from tinydb import where
from src.repositories import DocumentRepository
from src.models.user_data import Organization, User
import gc


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return str(tmp_path / "test_documents.json")


@pytest.fixture
def document_repo(temp_db_path):
    """Create a DocumentRepository instance with a temporary database."""
    repo = DocumentRepository(temp_db_path)
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
def sample_organization():
    """Create a sample organization for testing."""
    return Organization(
        id=None,
        name="Margravate Inc",
        email="contact@margravate.com",
        mail_suffixes=["@margravate.com", "@luxemburg.eu"],
    )


@pytest.fixture
def sample_user(sample_organization):
    """Create a sample user for testing."""
    return User(
        id=None, name="Jobst Luxemburg", organization=sample_organization
    )


class TestDocumentRepositoryBasicOperations:
    """Test basic CRUD operations of DocumentRepository."""

    def test_insert_document(self, document_repo):
        """Test inserting a single document."""
        doc = {"name": "Test Document", "value": 42}
        doc_id = document_repo.insert(doc)

        assert isinstance(doc_id, int)
        assert doc_id > 0

    def test_insert_multiple_documents(self, document_repo):
        """Test inserting multiple documents."""
        docs = [
            {"name": "Doc1", "value": 1},
            {"name": "Doc2", "value": 2},
            {"name": "Doc3", "value": 3},
        ]
        doc_ids = document_repo.insert_multiple(docs)

        assert len(doc_ids) == 3
        assert all(isinstance(doc_id, int) for doc_id in doc_ids)

    def test_get_all_documents(self, document_repo):
        """Test retrieving all documents."""
        docs = [{"name": f"Doc{i}"} for i in range(5)]
        document_repo.insert_multiple(docs)

        all_docs = document_repo.get_all()
        assert len(all_docs) == 5

    def test_search_documents(self, document_repo):
        """Test searching for documents."""
        document_repo.insert_multiple(
            [
                {"category": "A", "value": 10},
                {"category": "B", "value": 20},
                {"category": "A", "value": 30},
            ]
        )

        results = document_repo.search(where("category") == "A")
        assert len(results) == 2
        assert all(doc["category"] == "A" for doc in results)

    def test_update_documents(self, document_repo):
        """Test updating documents."""
        document_repo.insert({"name": "Original", "status": "pending"})

        updated_ids = document_repo.update(
            {"status": "completed"}, where("name") == "Original"
        )

        assert len(updated_ids) == 1
        result = document_repo.search(where("name") == "Original")[0]
        assert result["status"] == "completed"

    def test_remove_documents(self, document_repo):
        """Test removing documents."""
        document_repo.insert_multiple(
            [
                {"type": "temp", "id": 1},
                {"type": "temp", "id": 2},
                {"type": "keep", "id": 3},
            ]
        )

        removed_ids = document_repo.remove(where("type") == "temp")
        assert len(removed_ids) == 2

        remaining = document_repo.get_all()
        assert len(remaining) == 1
        assert remaining[0]["type"] == "keep"

    def test_count_documents(self, document_repo):
        """Test counting documents."""
        document_repo.insert_multiple(
            [{"active": True}, {"active": True}, {"active": False}]
        )

        total_count = document_repo.count()
        assert total_count == 3

        # Query for documents where active is True
        # Note: == True is correct for TinyDB query building
        active_count = document_repo.count(
            where("active") == True  # noqa: E712
        )
        assert active_count == 2


class TestOrganizationAndUserStorage:
    """Test storing Organization and User models in DocumentRepository."""

    def test_insert_organization(self, document_repo, sample_organization):
        """Test inserting an organization document."""
        org_dict = {
            "name": sample_organization.name,
            "email": sample_organization.email,
            "mail_suffixes": sample_organization.mail_suffixes,
        }

        org_id = document_repo.insert(org_dict, "organizations")
        assert org_id > 0

        stored_org = document_repo.get_by_id(org_id, "organizations")
        assert stored_org["name"] == "Margravate Inc"
        assert stored_org["email"] == "contact@margravate.com"
        assert "@margravate.com" in stored_org["mail_suffixes"]

    def test_insert_user_with_organization(
        self, document_repo, sample_organization, sample_user
    ):
        """Test inserting a user with organization."""
        # First insert organization
        org_dict = {
            "name": sample_organization.name,
            "email": sample_organization.email,
            "mail_suffixes": sample_organization.mail_suffixes,
        }
        org_id = document_repo.insert(org_dict, "organizations")

        # Then insert user
        user_dict = {
            "name": sample_user.name,
            "organization_id": org_id,
            "organization_name": sample_organization.name,
        }
        user_id = document_repo.insert(user_dict, "users")

        assert user_id > 0

        stored_user = document_repo.get_by_id(user_id, "users")
        assert stored_user["name"] == "Jobst Luxemburg"
        assert stored_user["organization_name"] == "Margravate Inc"

        # Verify organization mail suffixes are accessible
        stored_org = document_repo.get_by_id(org_id, "organizations")
        assert "@margravate.com" in stored_org["mail_suffixes"]
        assert "@luxemburg.eu" in stored_org["mail_suffixes"]

    def test_search_user_by_organization(
        self, document_repo, sample_organization
    ):
        """Test searching for users by organization."""
        # Insert organization
        org_dict = {
            "name": sample_organization.name,
            "email": sample_organization.email,
            "mail_suffixes": sample_organization.mail_suffixes,
        }
        org_id = document_repo.insert(org_dict, "organizations")

        # Insert multiple users
        users = [
            {
                "name": "Jobst Luxemburg",
                "organization_id": org_id,
                "organization_name": "Margravate Inc",
            },
            {
                "name": "Jane Doe",
                "organization_id": org_id,
                "organization_name": "Margravate Inc",
            },
            {
                "name": "John Smith",
                "organization_id": 999,
                "organization_name": "Other Corp",
            },
        ]
        document_repo.insert_multiple(users, "users")

        margravate_users = document_repo.search(
            where("organization_name") == "Margravate Inc", "users"
        )

        assert len(margravate_users) == 2
        user_names = [user["name"] for user in margravate_users]
        assert "Jobst Luxemburg" in user_names
        assert "Jane Doe" in user_names

    def test_update_organization_email_suffix(
        self, document_repo, sample_organization
    ):
        """Test updating organization email suffixes."""
        org_dict = {
            "name": sample_organization.name,
            "email": sample_organization.email,
            "mail_suffixes": ["@margravate.com"],
        }
        org_id = document_repo.insert(org_dict, "organizations")

        user_dict = {"name": "Jobst Luxemburg", "organization_id": org_id}
        document_repo.insert(user_dict, "users")

        # Update organization to add new email suffix
        document_repo.update(
            {
                "mail_suffixes": [
                    "@margravate.com",
                    "@luxemburg.eu",
                    "@jobst.de",
                ]
            },
            where("name") == "Margravate Inc",
            "organizations",
        )

        updated_org = document_repo.search(
            where("name") == "Margravate Inc", "organizations"
        )[0]

        assert len(updated_org["mail_suffixes"]) == 3
        assert "@jobst.de" in updated_org["mail_suffixes"]


class TestContextManager:
    """Test context manager functionality."""

    def test_context_manager(self, temp_db_path):
        """Test using DocumentRepository as context manager."""
        with DocumentRepository(temp_db_path) as repo:
            doc_id = repo.insert({"test": "data"})
            assert doc_id > 0

        # Verify database was closed and file exists
        assert Path(temp_db_path).exists()
