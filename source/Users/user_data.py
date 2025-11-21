from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[str]
    name: str
    email: str
    organization: str
