# PyDIT (Python Dependency Injection with Typing)

## Descrição

Usando PyDit você poderá fazer uso do princípio da inversão de dependências, usando classes abstratas ou protocolos para criar interfaces.

PyDit permite que seu código dependa somente de coisas abstratas, sem conhecer a implementação real.

## Instalação

**Usando poetry**

```zsh
poetry add pydit
```

**Usando pip**

```zsh
pip install pydit
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
from app.configs.di
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

**Chame a função de configurar as dependências no seu arquivo principal:**

> app/main.py

```python
from app.config.di import setup_dependencies()

setup_dependencies()
```

### Injetando dependencias em uma classe

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

## Features:

- [x] Injetar valores baseado na assinatura de tipos
- [x] Injetar valores baseado na herança de classes
- [x] Injetar valores via tokens
- [x] Resolve dependencias do tipo função, chamando a dependência e injetando seu resultado
- [ ] Injetar valores em funções ou construtores de classe `__init__` baseado na assinatura de argumentos
