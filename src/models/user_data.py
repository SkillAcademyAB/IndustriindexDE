from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Organization:
    """Organization model representing a company or entity.

    Attributes:
        id: Unique identifier for the organization. None if not yet assigned.
        name: Official name of the organization.
        email: Primary contact email address for the organization.
        mail_suffixes: List of valid email domain suffixes for the organization
            (e.g., ["@company.com", "@subsidiary.com"]).
    """
    id: Optional[str]
    name: str
    email: str
    mail_suffixes: List[str]


@dataclass
class User:
    """User model representing an individual within an organization.

    Attributes:
        id: Unique identifier for the user. None if not yet assigned.
        name: Full name of the user.
        organization: The Organization instance to which this user belongs.
    """
    id: Optional[str]
    name: str
    organization: Organization
