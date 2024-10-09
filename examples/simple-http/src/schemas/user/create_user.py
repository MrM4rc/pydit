from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class CreateUserSchema:
    name: str
    id: UUID = field(default_factory=uuid4)
    lastName: str | None = None
    email: str | None = None
