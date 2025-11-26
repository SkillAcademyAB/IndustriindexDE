from dataclasses import dataclass
from typing import Optional


@dataclass
class Organization:
    id: Optional[str]
    name: str
    email: str
    mail_suffixes: list[str]


@dataclass
class User:
    id: Optional[str]
    name: str
    organization: Organization
