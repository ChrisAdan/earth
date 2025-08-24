#!/usr/bin/env python3
"""
Tests for the main CLI application (app/main.py).
Tests CLI interface, user interaction simulation, and integration.
"""

import sys
from pathlib import Path
from unittest.mock import patch
import io

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "app"))

try:
    from app.main import EarthCLI
    from workflows import DatasetSpec
except ImportError as e:
    print(f"❌ Import error in test_main: {e}")
    sys.exit(1)


def test_cli_initialization():
    """Test CLI initialization and database setup."""
    print("🧪 Testing CLI initialization...")

    try:
        cli = EarthCLI()

        # Test initialization
        assert cli.conn is None, "Should start with no connection"
        assert cli.db_config is not None, "Should have database config"

        # Test database initialization
        cli.initialize_database()
        assert cli.conn is not None, "Should establish database connection"

        # Cleanup
        if cli.conn:
            cli.conn.close()

        print("✅ CLI initialization test passed")
        return True

    except Exception as e:
        print(f"❌ CLI initialization test failed: {e}")
        return False


def test_workflow_choice_validation():
    """Test workflow choice input validation."""
    print("🧪 Testing workflow choice validation...")

    try:
        cli = EarthCLI()

        # Mock user inputs - valid choice
        with patch("builtins.input", return_value="1"):
            choice = cli.get_workflow_choice()
            assert choice in [
                "people",
                "companies",
                "full_dataset",
            ], "Should return valid workflow"

        # Mock user inputs - invalid then valid
        with patch("builtins.input", side_effect=["invalid", "99", "2"]):
            with patch("builtins.print"):  # Suppress error messages
                choice = cli.get_workflow_choice()
                assert choice in [
                    "people",
                    "companies",
                    "full_dataset",
                ], "Should eventually return valid workflow"

        print("✅ Workflow choice validation test passed")
        return True

    except Exception as e:
        print(f"❌ Workflow choice validation test failed: {e}")
        return False


def test_single_workflow_parameters():
    """Test single workflow parameter collection."""
    print("🧪 Testing single workflow parameters...")

    try:
        cli = EarthCLI()
        cli.initialize_database()
        print(f"CLI and database initialized")
        # Test with default count
        with patch("builtins.input", return_value="1"):  # Use default
            with patch("builtins.print"):
                count, mode = cli.get_workflow_parameters("people")
                print(f"Got people parameters")
                assert isinstance(count, int), "Should return integer count"
                assert mode in ["append", "truncate"], "Should return valid write mode"
        print(f"Successful test with default count")
        # Test with custom count
        with patch("builtins.print"):
            with patch(
                "builtins.input", side_effect=["1", "50", "1"]
            ):  # Custom count, append mode
                count, mode = cli.get_workflow_parameters("companies")
                assert count == 50, "Should use custom count"
                assert mode == "append", "Should use append mode"
        print(f"Successful test with custom count")
        # Cleanup
        if cli.conn:
            cli.conn.close()

        print("✅ Single workflow parameters test passed")
        return True

    except Exception as e:
        print(f"❌ Single workflow parameters test failed: {e}")
        return False


def test_full_dataset_parameters():
    """Test full dataset parameter collection."""
    print("🧪 Testing full dataset parameters...")

    try:
        cli = EarthCLI()
        cli.initialize_database()

        # Test valid dataset parameters
        # with patch("builtins.print"):
        with patch(
            "builtins.input", side_effect=["1", "100", "10"]
        ):  # People, companies
            spec, mode = cli.get_workflow_parameters("full_dataset")
            # print('1. got here')
            assert isinstance(spec, DatasetSpec), "Should return DatasetSpec"
            assert spec.people_count == 100, "Should have correct people count"
            assert spec.companies_count == 10, "Should have correct company count"
            assert mode in ["append", "truncate"], "Should have valid write mode"
        # Test with defaults
        with patch("builtins.input", side_effect=["1", "", "", 'y']):  # Use defaults
            spec, mode = cli.get_workflow_parameters("full_dataset")
            # print('got here')
            assert spec.people_count == 1000, "Should use default people count"
            assert spec.companies_count == 100, "Should use default company count"

        # Cleanup
        if cli.conn:
            cli.conn.close()

        print("✅ Full dataset parameters test passed")
        return True

    except Exception as e:
        print(f"❌ Full dataset parameters test failed: {e}")
        return False


def test_workflow_execution():
    """Test workflow execution through CLI."""
    print("🧪 Testing workflow execution...")

    try:
        cli = EarthCLI()
        cli.initialize_database()

        # Test single workflow execution
        with patch("builtins.print"):  # Suppress output
            cli.execute_workflow("people", 5, "truncate")

        # Test full dataset execution
        spec = DatasetSpec(
            workflows={"people": 10, "companies": 2},
            description="Test execution dataset",
        )

        with patch("builtins.print"):
            cli.execute_workflow("full_dataset", spec, "truncate")

        # Cleanup
        if cli.conn:
            cli.conn.close()

        print("✅ Workflow execution test passed")
        return True

    except Exception as e:
        print(f"❌ Workflow execution test failed: {e}")
        return False


def test_cli_output_formatting():
    """Test CLI output formatting and display methods."""
    print("🧪 Testing CLI output formatting...")

    try:
        cli = EarthCLI()

        # Capture output
        captured_output = io.StringIO()

        with patch("sys.stdout", captured_output):
            cli.display_welcome()

        output = captured_output.getvalue()
        assert "EARTH" in output, "Should display Earth title"
        assert "Synthetic Data Generator" in output, "Should mention data generator"
        assert "workflows" in output.lower(), "Should mention workflows"

        print("✅ CLI output formatting test passed")
        return True

    except Exception as e:
        print(f"❌ CLI output formatting test failed: {e}")
        return False


def test_error_handling():
    """Test CLI error handling scenarios."""
    print("🧪 Testing CLI error handling...")

    try:
        cli = EarthCLI()

        # Test invalid workflow execution
        with patch("builtins.print"):  # Suppress error output
            try:
                cli.execute_workflow("invalid_workflow", 10, "truncate")
                # Should handle gracefully, not crash
            except SystemExit:
                assert False, "Should not cause system exit"

        # Test parameter validation
        with patch("builtins.input", side_effect=["0", "10"]):  # Invalid then valid
            with patch("builtins.print"):
                count, mode = cli.get_workflow_parameters("people")
                assert count == 10, "Should eventually get valid count"

        print("✅ CLI error handling test passed")
        return True

    except Exception as e:
        print(f"❌ CLI error handling test failed: {e}")
        return False


def test_end_to_end_simulation():
    """Test complete CLI workflow simulation."""
    print("🧪 Testing end-to-end CLI simulation...")

    try:
        # Simulate complete user interaction
        user_inputs = [
            "1",  # Choose people workflow
            "10",  # Generate 10 records
            "y",  # Confirm execution
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with patch("builtins.print"):  # Suppress output
                cli = EarthCLI()

                # Test individual components that would be called
                workflow_choice = cli.get_workflow_choice()
                assert workflow_choice == "people", "Should choose people workflow"

                # Initialize for parameter testing
                cli.initialize_database()

                # Get parameters manually since we're testing components
                count, mode = 10, "truncate"  # Simulate parameter collection

                # Test execution
                cli.execute_workflow(workflow_choice, count, mode)

                # Cleanup
                if cli.conn:
                    cli.conn.close()

        print("✅ End-to-end CLI simulation test passed")
        return True

    except Exception as e:
        print(f"❌ End-to-end CLI simulation test failed: {e}")
        return False


def main():
    """Run all main CLI tests."""
    print("🔄 Main CLI Tests")
    print("=" * 40)

    tests = [
        test_cli_initialization,
        test_workflow_choice_validation,
        test_single_workflow_parameters,
        test_full_dataset_parameters,
        test_workflow_execution,
        test_cli_output_formatting,
        test_error_handling,
        test_end_to_end_simulation,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1

    print(f"\n📊 Main CLI Tests - Passed: {passed}, Failed: {failed}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
