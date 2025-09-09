"""Test utilities and decorators for categorizing tests."""

import unittest
import functools
from typing import Callable, Any


def unit_test(func: Callable) -> Callable:
    """Decorator to mark a test as a unit test (no external dependencies)."""
    func._test_category = 'unit'
    return func


def integration_test(func: Callable) -> Callable:
    """Decorator to mark a test as an integration test (requires external services)."""
    func._test_category = 'integration'
    return func


def skip_if_no_services(func: Callable) -> Callable:
    """Decorator to skip test if required services are not running."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        from .conftest import check_services_running
        if not check_services_running():
            self.skipTest("Required services are not running. Start them with: docker compose up -d")
        return func(self, *args, **kwargs)
    return wrapper


class TestCategoryFilter:
    """Filter tests by category."""

    def __init__(self, categories: list[str] = None):
        self.categories = categories or ['unit', 'integration']

    def should_run_test(self, test_method: Callable) -> bool:
        """Check if a test method should be run based on its category."""
        category = getattr(test_method, '_test_category', 'unit')  # Default to unit
        return category in self.categories


def run_tests_by_category(test_class: type, categories: list[str] = None) -> unittest.TestResult:
    """Run tests from a class filtered by category."""
    filter_obj = TestCategoryFilter(categories)
    suite = unittest.TestSuite()

    for method_name in dir(test_class):
        method = getattr(test_class, method_name)
        if (method_name.startswith('test_') and
            callable(method) and
            filter_obj.should_run_test(method)):
            suite.addTest(test_class(method_name))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)
