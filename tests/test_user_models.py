import pytest
from source.models.user_data import Organization, User


class TestOrganizationModel:
    """Test Organization dataclass model."""

    def test_create_organization(self):
        """Test creating an Organization instance."""
        org = Organization(
            id=None,
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com"],
        )

        assert org.id is None
        assert org.name == "Margravate Inc"
        assert org.email == "contact@margravate.com"
        assert "@margravate.com" in org.mail_suffixes

    def test_organization_with_id(self):
        """Test creating an Organization with an ID."""
        org = Organization(
            id="org-123",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com"],
        )

        assert org.id == "org-123"
        assert org.name == "Margravate Inc"

    def test_organization_equality(self):
        """Test Organization equality comparison."""
        org1 = Organization(
            id="org-1",
            name="Test Org",
            email="test@org.com",
            mail_suffixes=["@testorg.com"],
        )
        org2 = Organization(
            id="org-1",
            name="Test Org",
            email="test@org.com",
            mail_suffixes=["@testorg.com"],
        )

        assert org1 == org2

    def test_organization_to_dict(self):
        """Test converting Organization to dictionary."""
        org = Organization(
            id="org-456",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com", "@margravate.eu"],
        )

        # Dataclasses don't have a built-in to_dict, but we can use __dict__
        org_dict = org.__dict__

        assert org_dict["id"] == "org-456"
        assert org_dict["name"] == "Margravate Inc"
        assert org_dict["email"] == "contact@margravate.com"
        assert len(org_dict["mail_suffixes"]) == 2


class TestUserModel:
    """Test User dataclass model."""

    @pytest.fixture
    def margravate_inc(self):
        """Fixture for Margravate Inc organization."""
        return Organization(
            id="org-margravate",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com", "@luxemburg.eu"],
        )

    def test_create_user(self, margravate_inc):
        """Test creating a User instance."""
        user = User(
            id=None,
            name="Jobst Luxemburg",
            organization=margravate_inc
        )

        assert user.id is None
        assert user.name == "Jobst Luxemburg"
        assert user.organization == margravate_inc
        assert len(user.organization.mail_suffixes) == 2
        assert "@margravate.com" in user.organization.mail_suffixes
        assert "@luxemburg.eu" in user.organization.mail_suffixes

    def test_user_with_id(self, margravate_inc):
        """Test creating a User with an ID."""
        user = User(
            id="user-jobst-001",
            name="Jobst Luxemburg",
            organization=margravate_inc
        )

        assert user.id == "user-jobst-001"
        assert user.name == "Jobst Luxemburg"

    def test_user_organization_relationship(self, margravate_inc):
        """Test User's relationship with Organization."""
        user = User(
            id=None, name="Jobst Luxemburg", organization=margravate_inc
        )

        assert user.organization.name == "Margravate Inc"
        assert user.organization.email == "contact@margravate.com"
        assert isinstance(user.organization, Organization)

    def test_user_organization_mail_suffixes(self):
        """Test accessing organization's email suffixes through user."""
        mail_suffixes = ["@margravate.com", "@luxemburg.eu", "@jobst.de"]

        org = Organization(
            id="org-1",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=mail_suffixes,
        )

        user = User(id=None, name="Jobst Luxemburg", organization=org)

        assert len(user.organization.mail_suffixes) == 3
        for suffix in mail_suffixes:
            assert suffix in user.organization.mail_suffixes

    def test_organization_empty_mail_suffixes(self):
        """Test Organization with empty mail suffixes list."""
        org = Organization(
            id="org-1", name="Test Org", email="test@org.com", mail_suffixes=[]
        )

        user = User(id=None, name="Jobst Luxemburg", organization=org)

        assert user.organization.mail_suffixes == []
        assert isinstance(user.organization.mail_suffixes, list)

    def test_user_equality(self, margravate_inc):
        """Test User equality comparison."""
        user1 = User(
            id="user-1",
            name="Jobst Luxemburg",
            organization=margravate_inc
            )
        user2 = User(
            id="user-1",
            name="Jobst Luxemburg",
            organization=margravate_inc
            )

        assert user1 == user2


class TestUserOrganizationIntegration:
    """Test integration between User and Organization models."""

    def test_jobst_luxemburg_at_margravate(self):
        """Test creating Jobst Luxemburg as employee of Margravate Inc."""
        # Create the organization
        margravate = Organization(
            id="org-margravate-001",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com", "@luxemburg.eu"],
        )

        # Create the user
        jobst = User(
            id="user-jobst-001",
            name="Jobst Luxemburg",
            organization=margravate
        )

        # Verify the relationship
        assert jobst.name == "Jobst Luxemburg"
        assert jobst.organization.name == "Margravate Inc"
        assert jobst.organization.email == "contact@margravate.com"
        assert "@margravate.com" in jobst.organization.mail_suffixes
        assert "@luxemburg.eu" in jobst.organization.mail_suffixes

    def test_multiple_users_same_organization(self):
        """Test multiple users belonging to the same organization."""
        margravate = Organization(
            id="org-margravate",
            name="Margravate Inc",
            email="contact@margravate.com",
            mail_suffixes=["@margravate.com"],
        )

        users = [
            User(id="user-1", name="Jobst Luxemburg", organization=margravate),
            User(id="user-2", name="Jane Margrave", organization=margravate),
        ]

        # All users should reference the same organization
        assert all(user.organization == margravate for user in users)
        assert all(
            user.organization.name == "Margravate Inc" for user in users
            )
        # All users share the same mail suffixes through the organization
        assert all(
            "@margravate.com" in user.organization.mail_suffixes
            for user in users
        )
