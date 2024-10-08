from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateUserModel:
    id: UUID
    name: str
    last_name: str | None = None
    email: str | None = None
