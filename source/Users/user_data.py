from dataclasses import dataclass
from typing import Optional


@dataclass
class Organization:
    id: Optional[str]
    name: str
    email: str
    organization: str


@dataclass
class User:
    id: Optional[str]
    name: str
    organization: Organization
    mail_suffixes: list[str]
