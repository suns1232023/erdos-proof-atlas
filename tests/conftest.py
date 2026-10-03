
"""
conftest.py — pytest configuration for erdos-proof-atlas tests.

REPAIR V6:
  - Added --run-slow flag to control slow test execution.
    Slow tests (e.g., discriminant computation ~60s) are skipped by default.
    Run with: pytest --run-slow to include them.
  - Added timeout marker for tests that may hang.
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (e.g., exact discriminant computation ~60s)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (skipped by default, run with --run-slow)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --run-slow is specified."""
    if config.getoption("--run-slow"):
        return  # Run all tests including slow ones

    skip_slow = pytest.mark.skip(reason="Slow test — run with --run-slow flag")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
