#!/usr/bin/env python3
"""
Earth Data Generator - Modular Test Suite
==========================================

This module provides a comprehensive test framework for the Earth Data Generator,
organized into logical modules that mirror the source code structure.

Test Structure:
- core/: Tests for database, utilities, and core functionality
- generators/: Tests for individual data generators (person, company, etc.)
- modules/: Tests for optional domain modules (companies, campaigns, automotive)
- app/: Tests for application layer (main, workflows, orchestration)

Usage:
    # Run all tests
    python -m pytest tests/

    # Run specific module tests
    python -m pytest tests/core/
    python -m pytest tests/generators/

    # Run with coverage
    python -m pytest tests/ --cov=src --cov=app

    # Run via make commands
    make test          # Full suite
    make test-core     # Core functionality only
    make test-gen      # Generators only
    make test-app      # Application layer only
"""

import sys
from pathlib import Path
from typing import Dict, List
import importlib.util

# Add project paths to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
app_path = project_root / "app"

sys.path.insert(0, str(src_path))
sys.path.insert(0, str(app_path))


class TestSuiteManager:
    """Manages test discovery, execution, and reporting across the modular test suite."""

    def __init__(self):
        self.test_root = Path(__file__).parent
        self.test_modules = {
            "core": self.test_root / "core",
            "generators": self.test_root / "generators",
            "modules": self.test_root / "modules",
            "app": self.test_root / "app",
        }
        self.available_tests = self._discover_tests()

    def _discover_tests(self) -> Dict[str, List[str]]:
        """Discover all available test modules."""
        discovered = {}

        for category, path in self.test_modules.items():
            if not path.exists():
                discovered[category] = []
                continue

            test_files = []
            for test_file in path.rglob("test_*.py"):
                relative_path = test_file.relative_to(self.test_root)
                test_files.append(
                    str(relative_path).replace("/", ".").replace(".py", "")
                )

            discovered[category] = sorted(test_files)

        return discovered

    def list_available_tests(self) -> None:
        """Print all available test modules."""
        print("🧪 Available Test Modules:")
        print("=" * 50)

        for category, tests in self.available_tests.items():
            if tests:
                print(f"\n📂 {category.upper()}:")
                for test in tests:
                    print(f"  • {test}")
            else:
                print(f"\n📂 {category.upper()}: (no tests found)")

    def run_category_tests(self, category: str, verbose: bool = False) -> bool:
        """Run all tests in a specific category."""
        if category not in self.available_tests:
            print(f"❌ Unknown test category: {category}")
            return False

        tests = self.available_tests[category]
        if not tests:
            print(f"⚠️  No tests found in category: {category}")
            return True

        print(f"🧪 Running {category.upper()} tests...")

        passed = 0
        failed = 0

        for test_module in tests:
            try:
                if verbose:
                    print(f"  Running {test_module}...")

                # Import and run the test
                success = self._run_test_module(test_module)
                if success:
                    passed += 1
                    if verbose:
                        print(f"  ✅ {test_module}")
                else:
                    failed += 1
                    if verbose:
                        print(f"  ❌ {test_module}")

            except Exception as e:
                failed += 1
                if verbose:
                    print(f"  ❌ {test_module} - {e}")

        print(f"📊 {category.upper()} Results: {passed} passed, {failed} failed")
        return failed == 0

    def _run_test_module(self, test_module: str) -> bool:
        """Run a specific test module."""
        try:
            # Convert dot notation back to file path
            test_path = self.test_root / f"{test_module.replace('.', '/')}.py"

            # Load and execute the test module
            spec = importlib.util.spec_from_file_location(test_module, test_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for main() function or run_tests() function
            if hasattr(module, "main"):
                return module.main()
            elif hasattr(module, "run_tests"):
                return module.run_tests()
            else:
                print(f"⚠️  No main() or run_tests() function found in {test_module}")
                return True

        except Exception as e:
            print(f"❌ Error running {test_module}: {e}")
            return False

    def run_all_tests(self, verbose: bool = False) -> Dict[str, bool]:
        """Run all tests across all categories."""
        print("🌍 Running Complete Earth Test Suite")
        print("=" * 60)

        results = {}

        for category in self.test_modules.keys():
            results[category] = self.run_category_tests(category, verbose)

        # Summary
        print("\n📈 Overall Test Results:")
        total_passed = sum(1 for success in results.values() if success)
        total_failed = len(results) - total_passed

        for category, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {category.upper()}")

        print(f"\n📊 Categories: {total_passed} passed, {total_failed} failed")

        return results


def get_test_dependencies() -> Dict[str, List[str]]:
    """Get test dependencies and check if they're available."""
    dependencies = {
        "core": ["pandas", "duckdb"],
        "generators": ["pandas", "faker"],
        "modules": ["pandas"],
        "app": ["pandas", "duckdb"],
    }

    missing = {}
    for category, deps in dependencies.items():
        missing_deps = []
        for dep in deps:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing_deps.append(dep)

        if missing_deps:
            missing[category] = missing_deps

    return missing


def check_test_environment() -> bool:
    """Check if the test environment is properly set up."""
    print("🔍 Checking test environment...")

    # Check paths
    if not src_path.exists():
        print(f"❌ Source path not found: {src_path}")
        return False

    if not app_path.exists():
        print(f"❌ App path not found: {app_path}")
        return False

    # Check dependencies
    missing = get_test_dependencies()
    if missing:
        print("⚠️  Missing dependencies:")
        for category, deps in missing.items():
            print(f"  {category}: {', '.join(deps)}")
        return False

    print("✅ Test environment check passed")
    return True


# Global test manager instance
test_manager = TestSuiteManager()


def run_quick_smoke_test() -> bool:
    """Run a quick smoke test to verify basic functionality."""
    print("🚀 Running quick smoke test...")

    try:
        # Test core imports
        from earth.core.loader import DatabaseConfig
        from earth.generators.person import generate_multiple_persons

        # Test basic generation
        persons = generate_multiple_persons(1, seed=42)
        assert len(persons) == 1, "Should generate one person"

        # Test database config
        db_config = DatabaseConfig.for_testing()
        assert db_config is not None, "Should create test database config"

        print("✅ Smoke test passed")
        return True

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False


# Convenience functions for different test categories
def run_core_tests(verbose: bool = False) -> bool:
    """Run core functionality tests."""
    return test_manager.run_category_tests("core", verbose)


def run_generator_tests(verbose: bool = False) -> bool:
    """Run data generator tests."""
    return test_manager.run_category_tests("generators", verbose)


def run_module_tests(verbose: bool = False) -> bool:
    """Run optional module tests."""
    return test_manager.run_category_tests("modules", verbose)


def run_app_tests(verbose: bool = False) -> bool:
    """Run application layer tests."""
    return test_manager.run_category_tests("app", verbose)


def run_all_tests(verbose: bool = False) -> bool:
    """Run the complete test suite."""
    results = test_manager.run_all_tests(verbose)
    return all(results.values())


if __name__ == "__main__":
    """Command-line interface for running tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Earth Data Generator Test Suite")
    parser.add_argument(
        "category",
        nargs="?",
        choices=["core", "generators", "modules", "app", "all"],
        default="all",
        help="Test category to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available tests"
    )
    parser.add_argument(
        "--check", "-c", action="store_true", help="Check test environment"
    )
    parser.add_argument(
        "--smoke", "-s", action="store_true", help="Run quick smoke test"
    )

    args = parser.parse_args()

    if args.list:
        test_manager.list_available_tests()
        sys.exit(0)

    if args.check:
        success = check_test_environment()
        sys.exit(0 if success else 1)

    if args.smoke:
        success = run_quick_smoke_test()
        sys.exit(0 if success else 1)

    # Run tests
    if args.category == "all":
        success = run_all_tests(args.verbose)
    elif args.category == "core":
        success = run_core_tests(args.verbose)
    elif args.category == "generators":
        success = run_generator_tests(args.verbose)
    elif args.category == "modules":
        success = run_module_tests(args.verbose)
    elif args.category == "app":
        success = run_app_tests(args.verbose)

    sys.exit(0 if success else 1)
