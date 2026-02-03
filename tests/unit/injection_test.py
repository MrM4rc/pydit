from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, cast
from typing_extensions import override
import unittest
from uuid import UUID, uuid4
import pydit
from pydit.core.dependencies import dependencies
from pydit.core.inject import FunctionInject
from pydit.exceptions.missing_default_value import MissingDefaultValueException

UserType = dict[str, Any]


class CircularDependencyA:
    def __init__(self, b: "CircularDependencyB" = FunctionInject()):
        self.b = b
        self.id = uuid4()


class CircularDependencyB:
    def __init__(self, a: CircularDependencyA = FunctionInject()):
        self.a = a
        self.id = uuid4()


class CircularDependencyC:
    def __init__(self, d: "CircularDependencyD" = FunctionInject()):
        self.d = d
        self.id = uuid4()


class CircularDependencyD:
    def __init__(self, e: "CircularDependencyE" = FunctionInject()):
        self.e = e
        self.id = uuid4()


class CircularDependencyE:
    def __init__(self, c: CircularDependencyC = FunctionInject()):
        self.c = c
        self.id = uuid4()


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

        self._create_users(service.repository)

        self._total_users_is_equal_to(service.repository, 3)

        self._users_equal_to(
            service.repository,
            [
                {"id": "uuid1", "name": "MrM4rc"},
                {"id": "uuid2", "name": "Foo"},
                {"id": "uuid3", "name": "Bar"},
            ],
        )

        self._user_equal_to(service.repository, "uuid1", {"id": "uuid1", "name": "MrM4rc"})

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

        self._create_users(service)
        self._total_users_is_equal_to(service.repository, 3)
        self._users_equal_to(
            service,
            [
                {"id": "uuid1", "name": "MrM4rc"},
                {"id": "uuid2", "name": "Foo"},
                {"id": "uuid3", "name": "Bar"},
            ],
        )

        self._user_equal_to(service, "uuid1", {"id": "uuid1", "name": "MrM4rc"})

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

        self._create_users(service)

        self._total_users_is_equal_to(service.repository, 3)
        self._users_equal_to(
            service,
            [
                {"id": "uuid1", "name": "MrM4rc"},
                {"id": "uuid2", "name": "Foo"},
                {"id": "uuid3", "name": "Bar"},
            ],
        )

        self._user_equal_to(service, "uuid1", {"id": "uuid1", "name": "MrM4rc"})

    def test_should_inject_a_callable_value(self):
        self.pydit.add_dependency(lambda: {"hello": "world"}, "callable")

        class MyService:
            @self.pydit.inject(token="callable")
            def some_prop(self) -> Callable[[], dict[str, Any]]:
                return cast(Any, None)

        self.assertEqual(MyService().some_prop(), {"hello": "world"})

    def test_should_inject_singleton_instance(self):
        class MyService:
            def __init__(self):
                self.id = uuid4()

        self.pydit.add_dependency(MyService)

        class Consumer:
            @self.pydit.inject(singleton=True)
            def service_a(self) -> MyService:
                return cast(Any, None)

            @self.pydit.inject(singleton=True)
            def service_b(self) -> MyService:
                return cast(Any, None)

            @self.pydit.inject()
            def service_c(self) -> MyService:
                return cast(Any, None)

        consumer = Consumer()

        self.assertEqual(consumer.service_a.id, consumer.service_b.id)

        self.assertIs(consumer.service_a, consumer.service_b)

        self.assertNotEqual(consumer.service_a.id, consumer.service_c.id)

        self.assertIsNot(consumer.service_a, consumer.service_c)

    def test_should_inject_value_by_constructor_inject(self):
        class MyService:
            def __init__(self, config: dict[str, Any] = FunctionInject(token="service_config")):
                self.config = config

        self.pydit.add_dependency({"key": "value"}, token="service_config")
        self.pydit.add_dependency(MyService)

        service = self.pydit.get_value(MyService)

        self.assertEqual(service.config, {"key": "value"})

    def test_should_inject_value_by_constructor_inject_with_no_token_or_type(self):
        class MyDependency:
            def say_hello(self) -> str:
                return "Hello!"

        class MyService:
            def __init__(self, dependency: MyDependency = FunctionInject()):
                self.dependency = dependency

        self.pydit.add_dependency(MyDependency)
        self.pydit.add_dependency(MyService)

        service = self.pydit.get_value(MyService)

        self.assertEqual(service.dependency.say_hello(), "Hello!")

    def test_should_inject_value_by_constructor_and_handle_default_value(self):
        class DependencyKlass:
            def say_hello(self) -> str:
                return "Hello!"

        class MyService:
            def __init__(
                self, test: int = 17, dep: DependencyKlass = FunctionInject(), name: str = "default_name"
            ):
                self.dep = dep
                self.name = name
                self.test = test

        self.pydit.add_dependency(DependencyKlass)
        self.pydit.add_dependency(MyService)

        service = self.pydit.get_value(MyService)

        self.assertEqual(service.dep.say_hello(), "Hello!")
        self.assertEqual(service.name, "default_name")
        self.assertEqual(service.test, 17)

    def test_should_throw_no_default_value_exception_when_no_default_value_is_provided(self):
        class MyService:
            def __init__(self, test: int, name: str = "default_name"):
                self.name = name
                self.test = test

        self.pydit.add_dependency(MyService)

        with self.assertRaises(MissingDefaultValueException):
            self.pydit.get_value(MyService)

    def test_should_resolve_circular_dependencies_with_one_level(self):
        self.pydit.add_dependency(CircularDependencyA)
        self.pydit.add_dependency(CircularDependencyB)

        a_instance = self.pydit.get_value(CircularDependencyA)

        self.assertIsInstance(a_instance, CircularDependencyA)
        self.assertIsInstance(a_instance.b, CircularDependencyB)
        self.assertTrue(a_instance.b.__is_proxy__())  # type: ignore
        self.assertEqual(a_instance.id, a_instance.b.a.id)

    def test_should_resolve_circular_dependencies_with_multiple_levels(self):
        self.pydit.add_dependency(CircularDependencyC)
        self.pydit.add_dependency(CircularDependencyD)
        self.pydit.add_dependency(CircularDependencyE)

        c_instance = self.pydit.get_value(CircularDependencyC)

        self.assertIsInstance(c_instance, CircularDependencyC)
        self.assertIsInstance(c_instance.d, CircularDependencyD)
        self.assertTrue(c_instance.d.__is_proxy__())  # type: ignore
        self.assertIsInstance(c_instance.d.e, CircularDependencyE)
        self.assertTrue(c_instance.d.e.__is_proxy__())  # type: ignore
        self.assertEqual(c_instance.id, c_instance.d.e.c.id)

    def test_should_resolve_circular_dependencies_using_inject_decorator(self):
        class ServiceA:
            @self.pydit.inject()
            def service_a(self) -> "CircularDependencyA":
                return cast(Any, None)

        self.pydit.add_dependency(CircularDependencyA)
        self.pydit.add_dependency(CircularDependencyB)

        service = ServiceA()

        self.assertIsInstance(service.service_a, CircularDependencyA)
        self.assertIsInstance(service.service_a.b, CircularDependencyB)
        self.assertTrue(service.service_a.b.__is_proxy__())  # type: ignore
        self.assertEqual(service.service_a.id, service.service_a.b.a.id)

    def test_should_inject_value_inside_function(self):
        self.pydit.add_dependency(
            {"host": "localhost", "port": 1234, "user": "user", "password": "teste"}, token="db_config"
        )

        class UrlParser(Protocol):
            @abstractmethod
            def parse(self, url: str) -> str:
                pass

        class RawUrlParser:
            def parse(self, url: str) -> str:
                return f"{url}-parsed"

        self.pydit.add_dependency(RawUrlParser)

        def test(db_config: dict[str, Any] = FunctionInject(token="db_config")):
            url = f"{db_config['host']}:{db_config['port']}"

            return url

        def test_2(test_fn: Callable[[], str] = FunctionInject(test), parser: UrlParser = FunctionInject()):
            url = test_fn()

            return parser.parse(url)

        self.pydit.add_dependency(test, token="test_fn")
        self.pydit.add_dependency(test_2, token="test_2")

        fn = self.pydit.get_value(type_=test, token="test_fn")
        fn2 = self.pydit.get_value(test_2)

        self.assertEqual(fn(), "localhost:1234")
        self.assertEqual(fn2(), "localhost:1234-parsed")

    def test_should_inject_value_inside_function_and_return_partial_function(self):
        self.pydit.add_dependency(
            {"host": "localhost", "port": 1234, "user": "user", "password": "teste"},
            "db_config",
        )

        def test(max_retry: int, db_config: dict[str, Any] = FunctionInject(token="db_config")):
            url = f"{db_config['host']}:{db_config['port']}-{max_retry}"

            return url

        self.pydit.add_dependency(test, token="test_fn")

        fn = self.pydit.get_value(type_=test, token="test_fn")

        self.assertEqual(fn(1), "localhost:1234-1")
        self.assertEqual(fn(17), "localhost:1234-17")

    def _create_users(self, user_service: Any) -> list[dict[str, Any]]:
        users = [
            {
                "id": "uuid1",
                "name": "MrM4rc",
            },
            {
                "id": "uuid2",
                "name": "Foo",
            },
            {
                "id": "uuid3",
                "name": "Bar",
            },
        ]

        for user in users:
            user_service.create(user)

        return users

    def _total_users_is_equal_to(self, user_service: Any, expected_total: int) -> None:
        users = user_service.list_()

        self.assertEqual(len(users), expected_total)

    def _users_equal_to(self, user_service: Any, expected_users: list[dict[str, Any]]) -> None:
        users = user_service.list_()

        self.assertEqual(users, expected_users)

    def _user_equal_to(self, user_service: Any, user_id: Any, expected_user: dict[str, Any]) -> None:
        user = user_service.get_by_id(user_id)

        self.assertEqual(user, expected_user)
