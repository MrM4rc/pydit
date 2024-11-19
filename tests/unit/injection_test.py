from abc import ABC, abstractmethod
from typing import Any, Protocol, cast
from typing_extensions import override
import unittest
from uuid import UUID, uuid4
import pydit
from pydit.core.dependencies import dependencies

UserType = dict[str, Any]


class InjectionTest(unittest.TestCase):
    @override
    def setUp(self):
        dependencies.clear()
        self.pydit = pydit.PyDit()

    def test_should_inject_by_token(self):
        self.pydit.add_dependency(
            {
                "host": "localhost",
                "port": 1234,
                "user": "user",
                "password": "teste",
            },
            token="db_credentials",
        )

        class MyDBService:
            @self.pydit.inject(token="db_credentials")
            def credentials(self) -> dict[str, Any]:
                return cast(Any, None)

        db_service = MyDBService()

        self.assertEqual(
            db_service.credentials,
            {
                "host": "localhost",
                "port": 1234,
                "user": "user",
                "password": "teste",
            },
        )

    def test_should_inject_by_subclass(self):

        class IUserRepository(ABC):
            @abstractmethod
            def create(self, data: UserType) -> None:
                pass

            @abstractmethod
            def get_by_id(self, id_: UUID) -> UserType:
                pass

            @abstractmethod
            def list_(self) -> list[UserType]:
                pass

        class UserRepository(IUserRepository):
            def __init__(self):
                print("Credentiaals ==>", self.credentials)

                self._users: list[dict[str, Any]] = []

            @self.pydit.inject(token="db_credentials")
            def credentials(self) -> dict[str, Any]:
                return cast(Any, None)

            @override
            def create(self, data: dict[str, Any]):
                self._users.append(data)

            @override
            def get_by_id(self, id_: UUID) -> dict[str, Any]:
                for user in self._users:
                    if user.get("id") != id_:
                        continue

                    return user

                raise ValueError("NotFound")

            @override
            def list_(self) -> list[UserType]:
                return self._users

        self.pydit.add_dependency(
            {
                "host": "localhost",
                "port": 1234,
                "user": "user",
                "password": "teste",
            },
            token="db_credentials",
        )
        self.pydit.add_dependency(UserRepository)

        class UserService:
            @self.pydit.inject()
            def repository(self) -> IUserRepository:
                return cast(Any, None)

            def create(self, user: dict[str, Any]):
                self.repository.create(user)

            def get_by_id(self, id_: UUID):
                return self.repository.get_by_id(id_)

            def list_(self):
                return self.repository.list_()

        service = UserService()
        user_1 = uuid4()
        user_2 = uuid4()
        user_3 = uuid4()

        service.create({"id": user_1, "name": "MrM4rc"})
        service.create({"id": user_2, "name": "Foo"})
        service.create({"id": user_3, "name": "Bar"})

        users = service.list_()

        self.assertEqual(len(users), 3)
        self.assertEqual(
            users,
            [
                {"id": user_1, "name": "MrM4rc"},
                {"id": user_2, "name": "Foo"},
                {"id": user_3, "name": "Bar"},
            ],
        )

        self.assertEqual(
            service.get_by_id(user_1), {"id": user_1, "name": "MrM4rc"}
        )

    def test_should_inject_by_protocol_with_inheritance(self):

        class IUserRepository(Protocol):
            @abstractmethod
            def create(self, data: UserType) -> None:
                pass

            @abstractmethod
            def get_by_id(self, id_: UUID) -> UserType:
                pass

            @abstractmethod
            def list_(self) -> list[UserType]:
                pass

        class UserRepository(IUserRepository):
            def __init__(self):
                print("Credentiaals ==>", self.credentials)

                self._users: list[dict[str, Any]] = []

            @self.pydit.inject(token="db_credentials")
            def credentials(self) -> dict[str, Any]:
                return cast(Any, None)

            @override
            def create(self, data: UserType):
                self._users.append(data)

            @override
            def get_by_id(self, id_: UUID) -> UserType:
                for user in self._users:
                    if user.get("id") != id_:
                        continue

                    return user

                raise ValueError("NotFound")

            @override
            def list_(self) -> list[UserType]:
                return self._users

        self.pydit.add_dependency(
            {
                "host": "localhost",
                "port": 1234,
                "user": "user",
                "password": "teste",
            },
            token="db_credentials",
        )
        self.pydit.add_dependency(UserRepository)

        class UserService:
            @self.pydit.inject()
            def repository(self) -> IUserRepository:
                return cast(Any, None)

            def create(self, user: dict[str, Any]):
                self.repository.create(user)

            def get_by_id(self, id_: UUID):
                return self.repository.get_by_id(id_)

            def list_(self):
                return self.repository.list_()

        service = UserService()
        user_1 = uuid4()
        user_2 = uuid4()
        user_3 = uuid4()

        service.create({"id": user_1, "name": "MrM4rc"})
        service.create({"id": user_2, "name": "Foo"})
        service.create({"id": user_3, "name": "Bar"})

        users = service.list_()

        self.assertEqual(len(users), 3)
        self.assertEqual(
            users,
            [
                {"id": user_1, "name": "MrM4rc"},
                {"id": user_2, "name": "Foo"},
                {"id": user_3, "name": "Bar"},
            ],
        )

        self.assertEqual(
            service.get_by_id(user_1), {"id": user_1, "name": "MrM4rc"}
        )

    def test_should_inject_by_protocol_without_inheritance(self):

        class IUserRepository(Protocol):
            @abstractmethod
            def create(self, data: UserType) -> None:
                pass

            @abstractmethod
            def get_by_id(self, id_: UUID) -> UserType:
                pass

            @abstractmethod
            def list_(self) -> list[UserType]:
                pass

        class UserRepository:
            def __init__(self):
                print("Credentiaals ==>", self.credentials)

                self._users: list[dict[str, Any]] = []

            @self.pydit.inject(token="db_credentials")
            def credentials(self) -> dict[str, Any]:
                return cast(Any, None)

            def create(self, data: UserType):
                self._users.append(data)

            def get_by_id(self, id_: UUID) -> UserType:
                for user in self._users:
                    if user.get("id") != id_:
                        continue

                    return user

                raise ValueError("NotFound")

            def list_(self) -> list[UserType]:
                return self._users

        self.pydit.add_dependency(
            {
                "host": "localhost",
                "port": 1234,
                "user": "user",
                "password": "teste",
            },
            token="db_credentials",
        )
        self.pydit.add_dependency(UserRepository)

        class UserService:
            @self.pydit.inject()
            def repository(self) -> IUserRepository:
                return cast(Any, None)

            def create(self, user: dict[str, Any]):
                self.repository.create(user)

            def get_by_id(self, id_: UUID):
                return self.repository.get_by_id(id_)

            def list_(self):
                return self.repository.list_()

        service = UserService()
        user_1 = uuid4()
        user_2 = uuid4()
        user_3 = uuid4()

        service.create({"id": user_1, "name": "MrM4rc"})
        service.create({"id": user_2, "name": "Foo"})
        service.create({"id": user_3, "name": "Bar"})

        users = service.list_()

        self.assertEqual(len(users), 3)
        self.assertEqual(
            users,
            [
                {"id": user_1, "name": "MrM4rc"},
                {"id": user_2, "name": "Foo"},
                {"id": user_3, "name": "Bar"},
            ],
        )

        self.assertEqual(
            service.get_by_id(user_1), {"id": user_1, "name": "MrM4rc"}
        )

    def test_should_inject_a_callable_value(self):
        self.pydit.add_dependency(lambda: {"hello": "world"}, "callable")

        class MyService:
            @self.pydit.inject(token="callable")
            def some_prop(self) -> dict[str, Any]:
                return {}

        self.assertEqual(MyService().some_prop, {"hello": "world"})
