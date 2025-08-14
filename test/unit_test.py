#!/usr/bin/env python3
"""
Unit test script for Earth's core functionality.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / "src"

try:
    from loader import DatabaseConfig, connect_to_duckdb, operate_on_table, log
    from generators.person import generate_multiple_persons
    import pandas as pd
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you've run 'make install' first!")
    print(f"Current Python path: {sys.path}")
    print(f"Looking for src at: {src_path}")
    sys.exit(1)

def test_person_generation():
    """Test person profile generation."""
    print("\n🧪 Testing person generation...")
    
    try:
        # Generate test persons with reproducible seed
        persons = generate_multiple_persons(3, seed=42)
        
        assert len(persons) == 3, "Should generate 3 persons"
        
        for person in persons:
            assert person.full_name, "Person should have a name"
            assert person.age >= 18, "Person should be adult"
            assert person.person_id, "Person should have ID"
        
        print("✅ Person generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Person generation test failed: {e}")
        return False


def test_database_operations():
    """Test database CRUD operations."""
    print("\n🧪 Testing database operations...")
    
    try:
        # Connect to test database
        conn = connect_to_duckdb(DatabaseConfig.for_testing())
        
        # Generate test data
        persons = generate_multiple_persons(2, seed=123)
        df = pd.DataFrame([person.to_dict() for person in persons])

        test_schema="test"
        
        # Test ping operation (table shouldn't exist yet)
        exists_before = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="ping"
        )
        assert not exists_before, "Test table shouldn't exist initially"
        
        # Test write operation
        operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="write",
            object_data=df,
            how="truncate"
        )
        
        # Test ping operation (table should exist now)
        exists_after = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="ping"
        )
        assert exists_after, "Test table should exist after write"
        
        # Test read operation
        result_df = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="read",
            query=f"SELECT COUNT(*) as count FROM {test_schema}.test_persons"
        )
        
        assert len(result_df) == 1, "Should get one row from count query"
        assert result_df['count'].iloc[0] == 2, "Should have 2 records"
        
        # Cleanup
        conn.execute(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE")
        conn.close()
        
        print("✅ Database operations test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False


def test_data_quality():
    """Test the quality and realism of generated data."""
    print("\n🧪 Testing data quality...")
    
    try:
        # Generate larger sample for quality testing
        persons = generate_multiple_persons(50, seed=456)
        
        # Test age distribution
        ages = [p.age for p in persons]
        assert min(ages) >= 18, "All persons should be adults"
        assert max(ages) <= 85, "Age should be reasonable"
        
        # Test email format
        emails = [p.email for p in persons]
        assert all('@' in email for email in emails), "All emails should have @"
        
        # Test income reasonableness
        incomes = [p.annual_income for p in persons]
        assert all(income >= 0 for income in incomes), "Income should be non-negative"
        assert any(income > 0 for income in incomes), "At least some should have income"
        
        print("✅ Data quality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False


def display_sample_data():
    """Display sample of generated data."""
    print("\n📊 Sample generated data:")
    
    persons = generate_multiple_persons(3, seed=789)
    
    for i, person in enumerate(persons, 1):
        print(f"\n👤 Person {i}:")
        print(f"  Name: {person.full_name} ({person.age} years old)")
        print(f"  Location: {person.city}, {person.state}")
        print(f"  Job: {person.job_title}")
        print(f"  Income: ${person.annual_income:,}")
        print(f"  Education: {person.education_level}")



def main():
    """Run all tests."""
    print("🌍 Earth Unit Tests")
    print("=" * 50)
    
    tests = [
        test_person_generation,
        test_database_operations,
        test_data_quality,
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
    
    # Show sample data
    display_sample_data()
    
    # Summary
    print(f"\n📈 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed! Earth is ready to go!")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)