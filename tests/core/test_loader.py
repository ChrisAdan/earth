#!/usr/bin/env python3
"""
Tests for earth.core.loader module.
Tests database connectivity, table operations, and data persistence.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "app"))

try:
    from earth.core.loader import (
        DatabaseConfig,
        connect_to_duckdb,
        operate_on_table,
        _ensure_schema_exists,
    )
    from earth.generators.person import generate_multiple_persons
except ImportError as e:
    print(f"❌ Import error in test_loader: {e}")
    sys.exit(1)


def test_database_config():
    """Test DatabaseConfig creation and methods."""
    print("🧪 Testing database configuration...")

    try:
        # Test development config
        dev_config = DatabaseConfig.for_dev()
        assert (
            str(dev_config.db_path) == "data/dev/earth_dev.duckdb"
        ), "Dev config should use earth_dev.duckdb"
        assert dev_config.schema_name == "raw", "Dev config should use raw schema"

        # Test testing config
        test_config = DatabaseConfig.for_testing()
        assert (
            str(test_config.db_path) == "data/dev/earth_dev.duckdb"
        ), "Test config should share earth_dev.duckdb"
        assert test_config.schema_name == "test", "Test config should use test schema"

        # Test production config
        prod_config = DatabaseConfig.for_prod()
        assert (
            str(prod_config.db_path) == "data/prod/earth_prod.duckdb"
        ), "Should use specified path"
        assert prod_config.schema_name == "raw", "Should use specified schema"

        print("✅ Database configuration tests passed")
        return True

    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        return False


def test_database_connection():
    """Test database connection functionality."""
    print("🧪 Testing database connection...")

    try:
        # Test connection creation
        config = DatabaseConfig.for_testing()
        conn = connect_to_duckdb(config)

        assert conn is not None, "Should create connection"

        # Test basic query
        result = conn.execute("SELECT 1 as test").fetchall()
        assert len(result) == 1, "Should execute simple query"
        assert result[0][0] == 1, "Should return correct result"

        conn.close()

        print("✅ Database connection tests passed")
        return True

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def test_schema_operations():
    """Test schema creation and management."""
    print("🧪 Testing schema operations...")

    try:
        config = DatabaseConfig.for_testing()
        conn = connect_to_duckdb(config)

        # Test schema creation
        _ensure_schema_exists(conn, "test_schema")

        # Verify schema exists
        schemas = conn.execute(
            f"""
                               SELECT schema_name from information_schema.schemata
                               where catalog_name = '{config.db_filename}'
                               """
        ).fetchall()
        schema_names = [row[0] for row in schemas]
        assert "test_schema" in schema_names, "Schema should be created"

        # Test idempotent schema creation
        _ensure_schema_exists(conn, "test_schema")  # Should not fail

        conn.close()

        print("✅ Schema operations tests passed")
        return True

    except Exception as e:
        print(f"❌ Schema operations test failed: {e}")
        return False


def test_table_operations():
    """Test table CRUD operations."""
    print("🧪 Testing table operations...")

    try:
        config = DatabaseConfig.for_testing()
        conn = connect_to_duckdb(config)

        # Generate test data
        persons = generate_multiple_persons(3, seed=42)
        df = pd.DataFrame([person.to_dict() for person in persons])

        test_schema = "test_ops"
        test_table = "test_persons"

        # Test ping (table doesn't exist yet - try clearing first)
        try:
            operate_on_table(
                conn=conn, schema_name=test_schema, table_name=test_table, action="drop"
            )
        except Exception as e:
            print(f"Failed to clear {test_schema}.{test_table}: {str(e)}")
        exists_before = operate_on_table(
            conn=conn, schema_name=test_schema, table_name=test_table, action="ping"
        )
        assert not exists_before, "Table shouldn't exist initially"

        # Test write operation
        operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name=test_table,
            action="write",
            object_data=df,
            how="truncate",
        )

        # Test ping (table should exist now)
        exists_after = operate_on_table(
            conn=conn, schema_name=test_schema, table_name=test_table, action="ping"
        )
        assert exists_after, "Table should exist after write"

        # Test read operation with count query
        count_df = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name=test_table,
            action="read",
            query=f"SELECT COUNT(*) as count FROM {test_schema}.{test_table}",
        )

        assert len(count_df) == 1, "Should get one row from count query"
        assert count_df["count"].iloc[0] == 3, "Should have 3 records"

        # Test read operation with data query
        data_df = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name=test_table,
            action="read",
            query=f"SELECT * FROM {test_schema}.{test_table} LIMIT 2",
        )

        assert len(data_df) == 2, "Should get 2 rows"
        assert "full_name" in data_df.columns, "Should have full_name column"
        assert "age" in data_df.columns, "Should have age column"

        # Test append operation
        more_persons = generate_multiple_persons(2, seed=123)
        more_df = pd.DataFrame([person.to_dict() for person in more_persons])

        operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name=test_table,
            action="write",
            object_data=more_df,
            how="append",
        )

        # Verify append worked
        final_count_df = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name=test_table,
            action="read",
            query=f"SELECT COUNT(*) as count FROM {test_schema}.{test_table}",
        )

        assert (
            final_count_df["count"].iloc[0] == 5
        ), "Should have 5 records after append"

        conn.close()

        print("✅ Table operations tests passed")
        return True

    except Exception as e:
        print(f"❌ Table operations test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in database operations."""
    print("🧪 Testing error handling...")

    try:
        config = DatabaseConfig.for_testing()
        conn = connect_to_duckdb(config)

        # Test reading from non-existent table
        try:
            operate_on_table(
                conn=conn,
                schema_name="nonexistent",
                table_name="nonexistent",
                action="read",
                query="SELECT * FROM nonexistent.nonexistent",
            )
            assert False, "Should raise error for non-existent table"
        except Exception:
            pass  # Expected error

        # Test invalid action
        try:
            operate_on_table(
                conn=conn,
                schema_name="test",
                table_name="test",
                action="invalid_action",
            )
            assert False, "Should raise error for invalid action"
        except ValueError as e:
            assert "Unknown action" in str(e), "Should mention unknown action"

        conn.close()

        print("✅ Error handling tests passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_data_types_and_persistence():
    """Test that different data types are properly handled and persisted."""
    print("🧪 Testing data types and persistence...")

    try:
        config = DatabaseConfig.for_testing()
        conn = connect_to_duckdb(config)

        # Create test data with various types
        test_data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "salary": [50000.50, 75000.75, 100000.00],
                "is_active": [True, False, True],
                "join_date": pd.to_datetime(["2020-01-01", "2021-06-15", "2022-12-31"]),
            }
        )

        # Write data
        operate_on_table(
            conn=conn,
            schema_name="types_test",
            table_name="mixed_types",
            action="write",
            object_data=test_data,
            how="truncate",
        )

        # Read data back
        result_df = operate_on_table(
            conn=conn,
            schema_name="types_test",
            table_name="mixed_types",
            action="read",
            query="SELECT * FROM types_test.mixed_types ORDER BY id",
        )

        # Verify data integrity
        assert len(result_df) == 3, "Should have 3 rows"
        assert result_df["name"].iloc[0] == "Alice", "String data should persist"
        assert result_df["age"].iloc[1] == 30, "Integer data should persist"
        assert (
            abs(result_df["salary"].iloc[2] - 100000.00) < 0.01
        ), "Float data should persist"

        conn.close()

        print("✅ Data types and persistence tests passed")
        return True

    except Exception as e:
        print(f"❌ Data types and persistence test failed: {e}")
        return False


def main():
    """Run all loader tests."""
    print("🗄️  Core Loader Tests")
    print("=" * 40)

    tests = [
        test_database_config,
        test_database_connection,
        test_schema_operations,
        test_table_operations,
        test_error_handling,
        test_data_types_and_persistence,
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

    print(f"\n📊 Loader Tests - Passed: {passed}, Failed: {failed}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
