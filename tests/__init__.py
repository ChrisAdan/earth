"""
Earth Data Generator Test Suite
==============================

This package provides comprehensive testing for the Earth synthetic data generator.
The test suite is organized into logical modules that mirror the source code structure.

Test Structure:
- core/: Tests for database, utilities, and core functionality  
- generators/: Tests for individual data generators (person, company, etc.)
- modules/: Tests for optional domain modules (companies, campaigns, automotive)
- app/: Tests for application layer (main, workflows, orchestration)

Usage:
    # Run all tests via pytest
    python -m pytest tests/
    
    # Run specific modules
    python -m pytest tests/core/
    python -m pytest tests/app/
    
    # Run via test runner
    python -m tests
    python tests/__main__.py
    
    # Run via make commands
    make test
    make test-core
    make test-app
"""

import sys
from pathlib import Path
from earth import __version__

# Ensure project paths are available
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
app_path = project_root / "app"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))

# Import test utilities that might be shared across test modules
try:
    from earth.core.loader import DatabaseConfig
    
    # Test configuration constants
    TEST_DB_CONFIG = DatabaseConfig.for_testing()
    TEST_SEED = 42
    TEST_BATCH_SIZE = 10
    
except ImportError:
    # Tests can still run without these, but may have reduced functionality
    TEST_DB_CONFIG = None
    TEST_SEED = 42
    TEST_BATCH_SIZE = 10

# Export commonly used test utilities
__all__ = [
    "TEST_DB_CONFIG",
    "TEST_SEED", 
    "TEST_BATCH_SIZE",
    "run_test_suite",
    "check_test_environment",
]


def run_test_suite(category=None, verbose=False):
    """
    Run tests for a specific category or all tests.
    
    Args:
        category: Test category ("core", "generators", "modules", "app", or None for all)
        verbose: Enable verbose output
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    from tests.__main__ import test_manager
    
    if category is None:
        results = test_manager.run_all_tests(verbose)
        return all(results.values())
    else:
        return test_manager.run_category_tests(category, verbose)


def check_test_environment():
    """
    Check if the test environment is properly configured.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    from tests.__main__ import check_test_environment as _check
    return _check()


# Convenience functions for interactive testing
def test_core(verbose=False):
    """Run core functionality tests."""
    return run_test_suite("core", verbose)


def test_generators(verbose=False):
    """Run data generator tests."""
    return run_test_suite("generators", verbose)


def test_modules(verbose=False):
    """Run optional module tests."""
    return run_test_suite("modules", verbose)


def test_app(verbose=False):
    """Run application layer tests."""
    return run_test_suite("app", verbose)


def test_all(verbose=False):
    """Run complete test suite."""
    return run_test_suite(None, verbose)


# Quick smoke test for development
def smoke_test():
    """Run a quick smoke test to verify basic functionality."""
    from tests.__main__ import run_quick_smoke_test
    return run_quick_smoke_test()