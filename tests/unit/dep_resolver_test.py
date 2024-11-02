from abc import abstractmethod
from typing import Literal, Protocol
from typing_extensions import override
import unittest
from pydit.core.register import injectable
from pydit.core.dependencies import dependencies
from pydit.core.resolver import DependencyResolver


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

        dep = self.resolver.resolve_dependencies(dict, token="db_credentials")

        self.assertEqual(
            dep.value,
            {"host": "localhost", "port": 1234, "user": "user", "password": "teste"},
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

        dep = self.resolver.resolve_dependencies(Test)

        self.assertEqual(dep.value, Subclass)

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

        dep = self.resolver.resolve_dependencies(Test)

        self.assertEqual(dep.value, Subclass)
