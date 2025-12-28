from abc import abstractmethod
from typing import Any, Literal, Protocol
from typing_extensions import override
import unittest
from pydit.core.inject import ConstructorInject
from pydit.core.register import injectable
from pydit.core.dependencies import Dependency, dependencies
from pydit.core.resolver import DependencyResolver
from pydit.exceptions.dependency_not_found import PyDitDependencyNotFoundException
from pydit.exceptions.no_default_value import MissingDefaultValueException
from pydit.utils.get_class_token import get_class_token


class CircularA:
    def __init__(self, b: "CircularB" = ConstructorInject()):
        self.b = b


class CircularB:
    def __init__(self, a: CircularA = ConstructorInject()):
        self.a = a


class CircularC:
    def __init__(self, d: "CircularD" = ConstructorInject()):
        self.d = d


class CircularD:
    def __init__(self, e: "CircularE" = ConstructorInject()):
        self.e = e


class CircularE:
    def __init__(self, c: CircularC = ConstructorInject()):
        self.c = c


class ResolverTest(unittest.TestCase):
    @override
    def setUp(self):
        dependencies.clear()
        self.resolver = DependencyResolver()

    def test_should_resolve_dependencies_by_token(self):
        injectable(
            {"host": "localhost", "port": 1234, "user": "user", "password": "teste"},
            token="db_credentials",
        )

        dep = self.resolver.resolve(None, token="db_credentials")

        self.assertEqual(
            dep,
            [
                (
                    Dependency(
                        {"host": "localhost", "port": 1234, "user": "user", "password": "teste"}, "db_credentials"
                    ),
                    [],
                )
            ],
        )

    def test_should_resolve_dependency_by_subclass(self):
        class Test:
            def hello(self):
                return "World"

            def meow(self):
                return "🐱"

        class Subclass(Test):
            """
            This class should be compatible with parent class by inheritance
            """

            def ops(self):
                pass

        injectable(Subclass)

        dep = self.resolver.resolve(Test)

        self.assertEqual(dep, [(Dependency(Subclass, get_class_token(Subclass)), [])])

    def test_should_resolve_dependency_by_protocol(self):
        """
        Should resolve dependencies by annotations/protocol typing
        """

        class Test(Protocol):
            @abstractmethod
            def hello(self) -> Literal["World"]:
                pass

            @abstractmethod
            def meow(self) -> Literal["🐱"]:
                pass

        class Subclass:
            """
            This class should be compatible with parent class by inheritance
            """

            def hello(self) -> Literal["World"]:
                return "World"

            def meow(self) -> Literal["🐱"]:
                return "🐱"

        injectable(Subclass)

        dep = self.resolver.resolve(Test)

        self.assertEqual(dep, [(Dependency(Subclass, get_class_token(Subclass)), [])])

    def test_should_not_resolve_incompatible_dependency_by_protocol(self):
        """
        Should not resolve dependencies by annotations/protocol typing
        """

        class Test(Protocol):
            @abstractmethod
            def hello(self) -> Literal["World"]:
                pass

            @abstractmethod
            def meow(self) -> Literal["🐱"]:
                pass

        class IncompatibleSubclass:
            """
            This class should be compatible with parent class by inheritance
            """

            def hello(self) -> Literal["World"]:
                return "World"

        injectable(IncompatibleSubclass)

        with self.assertRaises(PyDitDependencyNotFoundException):
            self.resolver.resolve(Test)

    def test_should_not_resolve_by_protocol_when_class_has_no_methods(self):
        """
        Should not resolve dependencies by annotations/protocol typing
        """

        class Test(Protocol):
            @abstractmethod
            def hello(self) -> Literal["World"]:
                pass

            @abstractmethod
            def meow(self) -> Literal["🐱"]:
                pass

        class IncompatibleSubclass:
            """
            This class should be compatible with parent class by inheritance
            """

            pass

        injectable(12, token="some_number")
        injectable(IncompatibleSubclass)

        with self.assertRaises(PyDitDependencyNotFoundException):
            self.resolver.resolve(Test)

    def test_should_throw_missing_default_value(self):
        class Test:
            def __init__(self, value: int):
                self.value = value

        injectable(Test)

        with self.assertRaises(MissingDefaultValueException) as context:
            self.resolver.resolve(Test)

        self.assertEqual("value", context.exception.parameter_name)

        class TestWithMultipleParams:
            def __init__(self, value: int, name: str = "default"):
                self.value = value
                self.name = name

        injectable(TestWithMultipleParams)

        with self.assertRaises(MissingDefaultValueException) as context:
            self.resolver.resolve(TestWithMultipleParams)

        self.assertEqual("value", context.exception.parameter_name)

    def test_should_resolve_dependency_with_constructor_params(self):
        injectable(30, token="refresh_time")
        injectable(
            {"host": "localhost", "port": 1234, "user": "user", "password": "teste"}, token="db_credentials"
        )

        class Test:
            def __init__(
                self,
                refresh_time: int = ConstructorInject(token="refresh_time"),
                db_credentials: dict[str, Any] = ConstructorInject(token="db_credentials"),
            ):
                self.refresh_time = refresh_time
                self.db_credentials = db_credentials

        injectable(Test)

        dep = self.resolver.resolve(Test)

        self.assertEqual(
            dep,
            [
                (
                    Dependency(
                        Test,
                        get_class_token(Test),
                    ),
                    [
                        (Dependency(30, "refresh_time"), []),
                        (
                            Dependency(
                                {"host": "localhost", "port": 1234, "user": "user", "password": "teste"},
                                "db_credentials",
                            ),
                            [],
                        ),
                    ],
                )
            ],
        )

    def test_should_resolve_circular_dependencies_with_one_level(self):

        injectable(CircularA)
        injectable(CircularB)

        dep = self.resolver.resolve(CircularA)

        self.assertEqual(
            dep,
            [
                (
                    Dependency(
                        CircularA,
                        get_class_token(CircularA),
                    ),
                    [
                        (
                            Dependency(
                                CircularB,
                                get_class_token(CircularB),
                            ),
                            [
                                (
                                    Dependency(
                                        CircularA,
                                        get_class_token(CircularA),
                                    ),
                                    [],
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    def test_should_resolve_circular_dependencies_with_multiple_levels(self):

        injectable(CircularC)
        injectable(CircularD)
        injectable(CircularE)

        dep = self.resolver.resolve(CircularC)

        print(dep)

        self.assertEqual(
            dep,
            [
                (
                    Dependency(
                        CircularC,
                        get_class_token(CircularC),
                    ),
                    [
                        (
                            Dependency(
                                CircularD,
                                get_class_token(CircularD),
                            ),
                            [
                                (
                                    Dependency(
                                        CircularE,
                                        get_class_token(CircularE),
                                    ),
                                    [
                                        (
                                            Dependency(
                                                CircularC,
                                                get_class_token(CircularC),
                                            ),
                                            [],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
