#!/usr/bin/env python3
"""
Unit test script for Earth's core functionality.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / "src"
app_path = project_root / "app"

sys.path.insert(0, str(src_path))
sys.path.insert(0, str(app_path))

try:
    from earth.core.loader import DatabaseConfig, connect_to_duckdb, operate_on_table
    from earth.generators.person import generate_multiple_persons
    import pandas as pd

    # Workflow imports
    from workflows import (
        WorkflowConfig,
        DatasetSpec,
        PeopleWorkflow,
        CompaniesWorkflow,
        FullDatasetWorkflow,
        list_available_workflows,
        create_workflow_from_name,
    )

    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you've run 'make install' first!")
    print(f"Current Python path: {sys.path}")
    print(f"Looking for src at: {src_path}")
    print(f"Looking for app at: {app_path}")
    sys.exit(1)


def test_workflow_registry():
    """Test workflow registry functionality."""
    print("\n🧪 Testing workflow registry...")

    try:
        # Test listing available workflows
        workflows = list_available_workflows()
        assert (
            len(workflows) >= 3
        ), f"Should have at least 3 workflows, got {len(workflows)}"
        assert "people" in workflows, "Should have people workflow"
        assert "companies" in workflows, "Should have companies workflow"
        assert "full_dataset" in workflows, "Should have full_dataset workflow"

        # Test workflow creation
        config = WorkflowConfig(batch_size=10, seed=42)

        people_workflow = create_workflow_from_name("people", config)
        assert isinstance(
            people_workflow, PeopleWorkflow
        ), "Should create PeopleWorkflow"

        companies_workflow = create_workflow_from_name("companies", config)
        assert isinstance(
            companies_workflow, CompaniesWorkflow
        ), "Should create CompaniesWorkflow"

        print("✅ Workflow registry test passed")
        return True

    except Exception as e:
        print(f"❌ Workflow registry test failed: {e}")
        return False

def test_people_workflow():
    """Test people workflow execution."""
    print("\n🧪 Testing people workflow...")

    try:
        # Create test configuration
        config = WorkflowConfig(batch_size=5, seed=123, write_mode="truncate")

        # Create workflow
        workflow = PeopleWorkflow(config, DatabaseConfig.for_testing())

        # Test batch generation
        batch_data = workflow.generate_batch(3)
        assert len(batch_data) == 3, "Should generate 3 records"

        # Validate batch data structure
        for record in batch_data:
            assert "person_id" in record, "Should have person_id"
            assert "full_name" in record, "Should have full_name"
            assert "age" in record, "Should have age"
            assert "job_title" in record, "Should have job_title"
            assert record["age"] >= 18, "Should be adult"

        # Test full workflow execution
        result = workflow.execute(10)

        assert result.success, f"Workflow should succeed: {result.error_message}"
        assert result.records_generated == 10, "Should generate 10 records"
        assert result.records_stored >= 10, "Should store at least 10 records"

        print("✅ People workflow test passed")
        return True

    except Exception as e:
        print(f"❌ People workflow test failed: {e}")
        return False

def test_companies_workflow():
    """Test companies workflow execution."""
    print("\n🧪 Testing companies workflow...")

    try:
        # Create test configuration
        config = WorkflowConfig(batch_size=3, seed=456, write_mode="truncate")

        # Create workflow
        workflow = CompaniesWorkflow(config, DatabaseConfig.for_testing())

        # Test batch generation
        batch_data = workflow.generate_batch(2)
        assert len(batch_data) == 2, "Should generate 2 records"

        # Validate batch data structure
        for record in batch_data:
            assert "company_id" in record, "Should have company_id"
            assert "company_name" in record, "Should have company_name"
            assert "industry" in record, "Should have industry"
            assert "employee_count" in record, "Should have employee_count"
            assert record["employee_count"] > 0, "Should have positive employee count"

        # Test full workflow execution
        result = workflow.execute(5)

        assert result.success, f"Workflow should succeed: {result.error_message}"
        assert result.records_generated == 5, "Should generate 5 records"
        assert result.records_stored >= 5, "Should store at least 5 records"

        print("✅ Companies workflow test passed")
        return True

    except Exception as e:
        print(f"❌ Companies workflow test failed: {e}")
        return False

def test_full_dataset_workflow():
    """Test full dataset workflow orchestration."""
    print("\n🧪 Testing full dataset workflow...")

    try:
        # Create test configuration
        config = WorkflowConfig(batch_size=5, seed=789, write_mode="truncate")

        # Create dataset specification
        dataset_spec = DatasetSpec(people_count=15, companies_count=3)

        # Create workflow
        workflow = FullDatasetWorkflow(
            config, DatabaseConfig.for_testing(), dataset_spec
        )

        # Test workflow properties
        assert workflow.workflow_name == "Full Dataset Generation"
        assert (
            len(workflow.workflow_steps) >= 2
        ), "Should have at least 2 workflow steps"

        # Test execution
        result = workflow.execute()

        assert (
            result.success
        ), f"Full dataset workflow should succeed: {result.error_message}"
        assert (
            result.records_generated >= 18
        ), "Should generate at least 18 total records"

        # Test execution summary
        summary = workflow.get_execution_summary()
        assert "workflow_steps" in summary, "Should have workflow steps in summary"
        assert "overall_stats" in summary, "Should have overall stats in summary"
        assert (
            summary["overall_progress"]["completed_steps"]
            == summary["overall_progress"]["total_steps"]
        )

        print("✅ Full dataset workflow test passed")
        return True

    except Exception as e:
        print(f"❌ Full dataset workflow test failed: {e}")
        return False

def test_data_quality_across_workflows():
    """Test data quality across different workflows."""
    print("\n🧪 Testing data quality across workflows...")

    try:
        config = WorkflowConfig(batch_size=10, seed=999)

        # Test people data quality
        people_workflow = PeopleWorkflow(config, DatabaseConfig.for_testing())
        people_batch = people_workflow.generate_batch(20)

        # Check age distribution
        ages = [record["age"] for record in people_batch]
        assert min(ages) >= 18, "All people should be adults"
        assert max(ages) <= 85, "Ages should be reasonable"

        # Check income distribution
        incomes = [record["annual_income"] for record in people_batch]
        assert all(income >= 0 for income in incomes), "Incomes should be non-negative"
        assert any(
            income > 30000 for income in incomes
        ), "Should have realistic income range"

        # Test companies data quality
        companies_workflow = CompaniesWorkflow(config, DatabaseConfig.for_testing())
        companies_batch = companies_workflow.generate_batch(10)

        # Check employee counts
        employee_counts = [record["employee_count"] for record in companies_batch]
        assert all(
            count > 0 for count in employee_counts
        ), "Should have positive employee counts"

        # Check revenue correlation with size
        revenues = [record["annual_revenue"] for record in companies_batch]
        assert all(rev >= 0 for rev in revenues), "Revenues should be non-negative"

        # Check business types
        business_types = [record["business_type"] for record in companies_batch]
        valid_types = [
            "Corporation",
            "LLC",
            "Partnership",
            "Sole Proprietorship",
            "S Corporation",
            "B Corporation",
            "Non-Profit",
            "Cooperative",
        ]
        assert all(
            bt in valid_types for bt in business_types
        ), "Should have valid business types"

        print("✅ Data quality test passed")
        return True

    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

def test_legacy_compatibility():
    """Test that legacy person generation still works."""
    print("\n🧪 Testing legacy compatibility...")

    try:
        # Test original person generation function
        persons = generate_multiple_persons(5, seed=42)

        assert len(persons) == 5, "Should generate 5 persons"

        for person in persons:
            assert person.full_name, "Person should have a name"
            assert person.age >= 18, "Person should be adult"
            assert person.person_id, "Person should have ID"
            assert person.job_title, "Person should have job title"

        print("✅ Legacy compatibility test passed")
        return True

    except Exception as e:
        print(f"❌ Legacy compatibility test failed: {e}")
        return False

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

        test_schema = "test"

        # Test ping operation (table shouldn't exist yet)
        exists_before = operate_on_table(
            conn=conn, schema_name=test_schema, table_name="test_persons", action="ping"
        )
        assert not exists_before, "Test table shouldn't exist initially"

        # Test write operation
        operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="write",
            object_data=df,
            how="truncate",
        )

        # Test ping operation (table should exist now)
        exists_after = operate_on_table(
            conn=conn, schema_name=test_schema, table_name="test_persons", action="ping"
        )
        assert exists_after, "Test table should exist after write"

        # Test read operation
        result_df = operate_on_table(
            conn=conn,
            schema_name=test_schema,
            table_name="test_persons",
            action="read",
            query=f"SELECT COUNT(*) as count FROM {test_schema}.test_persons",
        )

        assert len(result_df) == 1, "Should get one row from count query"
        assert result_df["count"].iloc[0] == 2, "Should have 2 records"

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
        assert all("@" in email for email in emails), "All emails should have @"

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
    """Display sample of generated data from workflows."""
    print("\n📊 Sample workflow-generated data:")

    try:
        config = WorkflowConfig(batch_size=5, seed=12345)

        # Sample people data
        people_workflow = PeopleWorkflow(config)
        people_data = people_workflow.generate_batch(2)

        print("\n👥 Sample People:")
        for i, person in enumerate(people_data, 1):
            print(f"  {i}. {person['full_name']} ({person['age']} years old)")
            print(
                f"     Job: {person['job_title']} | Income: ${person['annual_income']:,}"
            )
            print(f"     Location: {person['city']}, {person['state']}")

        # Sample companies data
        companies_workflow = CompaniesWorkflow(config)
        companies_data = companies_workflow.generate_batch(2)

        print("\n🏢 Sample Companies:")
        for i, company in enumerate(companies_data, 1):
            print(f"  {i}. {company['company_name']}")
            print(
                f"     Industry: {company['industry']} | Size: {company['company_size']}"
            )
            print(
                f"     Employees: {company['employee_count']:,} | Revenue: ${company['annual_revenue']:,}"
            )
            print(
                f"     Location: {company['headquarters_city']}, {company['headquarters_state']}"
            )

    except Exception as e:
        print(f"❌ Error generating sample data: {e}")

def main():
    """Run all tests."""
    print("🌍 Earth Enhanced Unit Tests")
    print("=" * 60)

    tests = [
        test_database_operations,
        test_workflow_registry,
        test_people_workflow,
        test_companies_workflow,
        test_full_dataset_workflow,
        test_data_quality,
        test_data_quality_across_workflows,
        test_legacy_compatibility,
        test_person_generation,
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
        print(f"\n🎉 All tests passed! Earth workflow system is ready!")
        print(f"💡 Available workflows: {', '.join(list_available_workflows())}")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
