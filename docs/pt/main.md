# PyDIT (Python Dependency Injection with Typing)

## Descrição

Usando PyDit você poderá fazer uso do princípio da inversão de dependências, usando classes abstratas ou protocolos para criar interfaces.

PyDit permite que seu código dependa somente de coisas abstratas, sem conhecer a implementação real.

## Instalação

**Usando poetry**

```zsh
poetry add python-pydit
```

**Usando pip**

```zsh
pip install python-pydit
```

## Uso

Primeiro, vamos criar a instância do PyDit:

> app/configs/di.py

```python
from pydit import PyDit

pydit = PyDit()
```

Em seguida vamos importar a instância do PyDit e registrar as dependências:

> app/configs/dependencies.py

```python
from typing import Any
from app.configs.di import pydit
from app.adapters.repositories.sqlalchemy.user_repository import SqlalchemyUserRepository
from app.configs.database import get_db_config

def setup_dependencies():
  """
  Isso é apenas uma sugestão, você pode configura-las da maneira que preferir
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

**Chame a função para configurar as dependências no seu arquivo principal:**

> app/main.py

```python
from app.config.di import setup_dependencies()

setup_dependencies()
```

## Injectando Dependências

### Injetando usando python e seu @property decorator

PyDIT suporta injeção de dependência similar ao funcionamento do @property do python.

> app/domain/user/services/create.py

```python
from typing import cast, Any
from app.configs.di import pydit
# Esta classse pode ser um protocol ou uma class que herda de ABC
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

Como podemos ver no exemplo, a classe CreateUserService desconhece a existência da classe `SqlalchemyUserRepository`,<br />
dependendo somente da intarface `IUserRepository`

### Injetando dependências por construtor

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

PyDIT consegue resolver dependências de funções definidas pelo usuário.

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

Para utilizar o princípio singleton, basta passar o parâmetro singleton como true na função inject

```python
from typing import cast, Any
from app.configs.di import pydit
# Esta classse pode ser um protocol ou uma class que herda de ABC
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

- [x] Injetar valores baseado na assinatura de tipos
- [x] Injetar valores baseado na herança de classes
- [x] Injetar valores via tokens
- [x] Resolve dependencias do tipo função, chamando a dependência e injetando seu resultado
- [x] Suporte ao singleton
- [x] Injetar valores em funções ou construtores de classe `__init__` baseado na assinatura de argumentos
- [ ] Adicionar suporte à kwargs quando injetando valores em funções
