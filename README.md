# PyDIT (Python Dependency Injection with Typing)

## Translations

[Português](./docs/pt/main.md)

## Description

With PyDit you can use ABC and Protocol to make interfaces and use the power of Dependency Inversion Principle.<br />

PyDit allow your code to depend only abstract things, not the real implementation.

## Install

**With poetry**

```zsh
poetry add python-pydit
```

**With pip**

```zsh
pip install python-pydit
```

## Usage

Create the PyDit instance:

> app/configs/di.py

```python
from pydit import PyDit

pydit = PyDit()
```

Import the pydit instance and register your project's dependencies:

> app/configs/dependencies.py

```python
from typing import Any
from app.configs.di import pydit
from app.adapters.repositories.sqlalchemy.user_repository import SqlalchemyUserRepository
from app.configs.database import get_db_config


def setup_dependencies():
  """
  This is only a suggestion, you're free to configure it like you want
  """

  dependencies: list[dict[str, Any]] = [
    {
      "dependency": SqlalchemyUserRepository,
      "token": "sqlalchemy_user_repository"
    },
    {
      "dependency": get_db_config,
      "token": "database_config",
    },
    {
      "dependency": "HELLO WORLD",
      "token": "test"
    }
  ]

  for dependency in dependencies:
    pydit.add_dependency(dependency["dependency"], dependency.get("token"))
```

**Call the setup_dependencies in the main file**

> app/main.py

```python
from app.config.di import setup_dependencies()

setup_dependencies()
```

### Injecting dependencies

#### Inject by property

Pydit supports python's @property decorator.

> app/domain/user/services/create.py

```python
from typing import cast, Any
from app.configs.di import pydit
# This class can be a Protocol or a clas that inherits from ABC
from app.adapters.repositories.interfaces.user_repositgory import IUserRepository

class CreateUserService:
  @pydit.inject()
  def user_repository(self) -> IUserRepository:
    return cast(IUserRepository, None)

  @pydit.inject(token="test")
  def other_property(self) -> str:
    return ""

  def execute(self, data: dict[str, Any]):
    self.user_repository.create(data)

    # Prints HELLO WORLD
    print(self.other_property)
```

How you can see, we're depending on the intarface `IUserRepository`, not the real `SqlalchemyUserRepository` implementation.

#### Inject dependencies by constuctor

> app/domain/user/services/create.py

```python
from pydit import FunctionInject
from app.adapters.repositories.interfaces.user_repositgory import IUserRepository

class CreateUserService:
  def __init__(
    self,
    user_repository: IUserRepository = FunctionInject(),
    other_property: str = FunctionInject(token="test")
  ):
    self.user_repository = user_repository

  def execute(self, data):
    self.user_repository.create(data)

    # Prints HELLO WORLD
    print(other_property)
```

#### Inject dependencies by function

PyDIT needs that each parameter of class/function have default value to be resolved

> app/domain/user/services/create.py

```python
from typing import Any
from pydit import FunctionInject
from app.adapters.repositories.interfaces.user_repositgory import IUserRepository

def create_user(user_data: dict[str, Any], repository: IUserRepository = FunctionInject()):
  repository.create(user_data)
```

> app/config/dependencies.py

```python
from app.configs.di import pydit
from app.domain.user.services.create import create_user

def setup_dependencies():
  pydit.add_dependency(create_user, "create_user")
```

> app/routers/v1/user.py

```python
from fastapi import APIRouter
from app.configs.di import pydit
from app.domain.user.dto.create import CreateUserDTO


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("")
def create(data: CreateUserDTO):
  create_service = pydit.get_value(token="create_user")
  create_service(data.dict())

  return "OK"
```

### Singleton

To use singleton approach, pass true to `singleton` parameter in inject fn.

```python
from typing import cast, Any
from app.configs.di import pydit
# This class can be a Protocol or a clas that inherits from ABC
from app.adapters.repositories.interfaces.user_repositgory import IUserRepository

class CreateUserService:
  @pydit.inject(singleton=True)
  def user_repository(self) -> IUserRepository:
    return cast(IUserRepository, None)

  @pydit.inject(token="test")
  def other_property(self) -> str:
    return ""

  def execute(self, data: dict[str, Any]):
    self.user_repository.create(data)

    # Prints HELLO WORLD
    print(self.other_property)
```

## Features:

- [x] Inject values based on type signature
- [x] Inject values based on inheritance
- [x] Inject values via token
- [x] Resolves function dependencies, calling and injecting the call result
- [x] Singleton support
- [x] Inject values in function calls or class constructor `__init__` based on the arguments' signatures
- [ ] Add support for kwargs when inject values in functions
