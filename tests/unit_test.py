#!/usr/bin/env python3
"""
Enhanced unit test script for Earth's refactored workflow system.
Tests the new dataset orchestration and unified workflow architecture.
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

    # Updated workflow imports for refactored system
    from workflows import (
        WorkflowConfig,
        DatasetSpec,
        PeopleWorkflow,
        CompaniesWorkflow,
        list_dataset_templates,
        create_workflow_from_name,
        create_entity_workflow,
        create_dataset_workflow,
        UnifiedWorkflowRegistry,
        get_template_info,
        validate_dataset_spec,
        print_system_summary,
        quick_generate_people,
        quick_generate_companies,
        quick_generate_dataset,
    )

    # New orchestrator imports
    from workflows.dataset_orchestrator import (
        DatasetOrchestrator,
        WorkflowStep,
        WorkflowStepStatus,
        DatasetWorkflow,
    )

    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you've run 'make install' first!")
    print(f"Current Python path: {sys.path}")
    print(f"Looking for src at: {src_path}")
    print(f"Looking for app at: {app_path}")
    sys.exit(1)


def test_new_dataset_orchestrator():
    """Test the new dataset orchestration system."""
    print("\n🧪 Testing dataset orchestrator...")

    try:
        # Test dataset specification creation and validation
        spec = DatasetSpec(
            workflows={"companies": 5, "people": 25},
            dependencies={"people": ["companies"]},
            description="Test dataset with dependencies",
        )

        spec.validate()
        assert spec.workflows["companies"] == 5, "Should have correct company count"
        assert spec.workflows["people"] == 25, "Should have correct people count"
        assert spec.dependencies["people"] == [
            "companies"
        ], "Should have correct dependencies"

        # Test execution order calculation
        execution_order = spec.get_execution_order()
        assert len(execution_order) == 2, "Should have 2 execution groups"
        assert "companies" in execution_order[0], "Companies should be in first group"
        assert "people" in execution_order[1], "People should be in second group"

        # Test orchestrator creation
        config = WorkflowConfig(batch_size=3, seed=123, write_mode="truncate")
        orchestrator = DatasetOrchestrator(
            spec, config, DatabaseConfig.for_testing(), max_parallel_workflows=2
        )

        assert len(orchestrator.workflow_steps) == 2, "Should have 2 workflow steps"
        assert "companies" in orchestrator.workflow_steps, "Should have companies step"
        assert "people" in orchestrator.workflow_steps, "Should have people step"

        # Test orchestrator execution
        summary = orchestrator.execute(use_parallel=False)  # Use sequential for testing

        assert (
            summary["execution_summary"]["overall_status"] == "completed"
        ), "Should complete successfully"
        assert (
            summary["execution_summary"]["total_records_generated"] >= 30
        ), "Should generate at least 30 records"
        assert (
            summary["performance_metrics"]["workflows_completed"] == 2
        ), "Should complete 2 workflows"
        assert (
            summary["performance_metrics"]["workflows_failed"] == 0
        ), "Should have no failures"

        print("✅ Dataset orchestrator test passed")
        return True

    except Exception as e:
        print(f"❌ Dataset orchestrator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_dataset_workflow_wrapper():
    """Test the DatasetWorkflow wrapper class."""
    print("\n🧪 Testing dataset workflow wrapper...")

    try:
        # Test with default dataset spec
        config = WorkflowConfig(batch_size=5, seed=456, write_mode="truncate")
        workflow = DatasetWorkflow(config, DatabaseConfig.for_testing())

        assert (
            "Dataset Generation" in workflow.workflow_name
        ), "Should have dataset workflow name"
        assert workflow.schema_name == "raw", "Should target raw schema"
        assert workflow.table_name == "dataset_metadata", "Should use metadata table"

        # Test execution
        result = workflow.execute()

        assert (
            result.success
        ), f"Dataset workflow should succeed: {result.error_message}"
        assert (
            result.records_generated >= 550
        ), "Should generate at least 550 records (500 people + 50 companies)"

        # Test execution summary
        summary = workflow.get_execution_summary()
        assert "execution_summary" in summary, "Should have execution summary"
        assert "workflow_steps" in summary, "Should have workflow steps"

        print("✅ Dataset workflow wrapper test passed")
        return True

    except Exception as e:
        print(f"❌ Dataset workflow wrapper test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_template_system():
    """Test the dataset template system."""
    print("\n🧪 Testing dataset template system...")

    try:
        # Test listing templates
        templates = list_dataset_templates()
        assert len(templates) >= 3, "Should have at least 3 templates"
        assert "small_demo" in templates, "Should have small_demo template"
        assert "medium_dev" in templates, "Should have medium_dev template"

        # Test template info retrieval
        template_info = get_template_info("small_demo")
        assert "description" in template_info, "Should have description"
        assert "workflows" in template_info, "Should have workflows"
        assert "people" in template_info["workflows"], "Should include people workflow"
        assert (
            "companies" in template_info["workflows"]
        ), "Should include companies workflow"

        # Test dataset creation from template
        config = WorkflowConfig(batch_size=5, seed=789, write_mode="truncate")
        dataset_workflow = create_dataset_workflow(
            template_name="small_demo",
            config=config,
            db_config=DatabaseConfig.for_testing(),
        )

        assert (
            dataset_workflow is not None
        ), "Should create dataset workflow from template"

        # Test execution
        result = dataset_workflow.execute()
        assert (
            result.success
        ), f"Template-based workflow should succeed: {result.error_message}"

        print("✅ Template system test passed")
        return True

    except Exception as e:
        print(f"❌ Template system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_validation_system():
    """Test the enhanced validation system."""
    print("\n🧪 Testing validation system...")

    try:
        # Test valid dataset spec
        valid_spec = DatasetSpec(
            workflows={"companies": 10, "people": 100},
            dependencies={"people": ["companies"]},
            description="Valid test dataset",
        )

        errors = validate_dataset_spec(valid_spec)
        assert len(errors) == 0, f"Valid spec should have no errors: {errors}"

        # Test invalid workflow reference
        invalid_workflow_spec = DatasetSpec(
            workflows={"nonexistent": 10, "people": 100},
            description="Invalid workflow reference",
        )

        errors = validate_dataset_spec(invalid_workflow_spec)
        print(f'Errors:\n{errors}')
        assert len(errors) > 0, "Should have errors for unknown workflow"
        assert any(
            "nonexistent" in error for error in errors
        ), "Should mention unknown workflow"

        print("✅ Validation system test passed")
        return True

    except Exception as e:
        print(f"❌ Validation system test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_quick_generation_functions():
    """Test the quick generation convenience functions."""
    print("\n🧪 Testing quick generation functions...")

    try:
        # Test quick people generation
        people_data = quick_generate_people(5, seed=111)
        assert len(people_data) == 5, "Should generate 5 people"
        assert "full_name" in people_data[0], "Should have full_name field"
        assert "age" in people_data[0], "Should have age field"

        # Test quick companies generation
        companies_data = quick_generate_companies(3, seed=222)
        assert len(companies_data) == 3, "Should generate 3 companies"
        assert "company_name" in companies_data[0], "Should have company_name field"
        assert "industry" in companies_data[0], "Should have industry field"

        # Test quick dataset generation
        dataset = quick_generate_dataset("small_demo", seed=333)
        assert "person" in dataset, "Should have person data"
        assert "company" in dataset, "Should have company data"
        assert (
            len(dataset["person"]) == 50
        ), "Should have 50 people from small_demo template"
        assert (
            len(dataset["company"]) == 10
        ), "Should have 10 companies from small_demo template"

        print("✅ Quick generation functions test passed")
        return True

    except Exception as e:
        print(f"❌ Quick generation functions test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_enhanced_entity_workflows():
    """Test the enhanced entity workflow features."""
    print("\n🧪 Testing enhanced entity workflows...")

    try:
        config = WorkflowConfig(batch_size=5, seed=444, write_mode="truncate")

        # Test person workflow with detailed stats
        person_workflow = create_entity_workflow(
            "person", config, DatabaseConfig.for_testing()
        )

        # Test batch generation and validation
        batch_data = person_workflow.generate_batch(3)
        assert len(batch_data) == 3, "Should generate 3 person records"

        # Test statistics generation
        stats = person_workflow.get_generation_statistics(batch_data)
        assert stats["entity_type"] == "person", "Should have correct entity type"
        assert stats["batch_size"] == 3, "Should have correct batch size"
        assert "person_stats" in stats, "Should have person-specific statistics"
        assert "age_range" in stats["person_stats"], "Should have age range statistics"

        # Test execution with detailed stats
        detailed_result = person_workflow.execute_with_detailed_stats(10)
        assert "workflow_result" in detailed_result, "Should have workflow result"
        assert "workflow_info" in detailed_result, "Should have workflow info"
        assert "configuration" in detailed_result, "Should have configuration info"
        assert detailed_result["workflow_result"][
            "success"
        ], "Should execute successfully"

        # Test company workflow
        company_workflow = create_entity_workflow(
            "company", config, DatabaseConfig.for_testing()
        )
        company_batch = company_workflow.generate_batch(2)

        company_stats = company_workflow.get_generation_statistics(company_batch)
        assert (
            "company_stats" in company_stats
        ), "Should have company-specific statistics"
        assert (
            "employee_range" in company_stats["company_stats"]
        ), "Should have employee range"

        print("✅ Enhanced entity workflows test passed")
        return True

    except Exception as e:
        print(f"❌ Enhanced entity workflows test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_parallel_execution():
    """Test parallel execution capabilities."""
    print("\n🧪 Testing parallel execution...")

    try:
        # Create dataset with multiple independent workflows for parallel execution
        spec = DatasetSpec(
            workflows={"companies": 20, "people": 50},
            dependencies={},  # No dependencies - can run in parallel
            description="Parallel execution test",
        )

        config = WorkflowConfig(batch_size=10, seed=555)
        orchestrator = DatasetOrchestrator(
            spec, config, DatabaseConfig.for_testing(), max_parallel_workflows=2
        )

        # Execute with parallelism enabled
        summary = orchestrator.execute(use_parallel=True)

        assert (
            summary["execution_summary"]["overall_status"] == "completed"
        ), "Should complete successfully"

        # Check that time was potentially saved by parallelism
        time_saved = summary["execution_summary"]["time_saved_by_parallelism"]
        parallel_efficiency = summary["execution_summary"]["parallel_efficiency"]

        # With no dependencies, we should see some parallelism benefit
        assert parallel_efficiency >= 1.0, "Parallel efficiency should be at least 1.0"

        print(f"    Parallel efficiency: {parallel_efficiency:.2f}x")
        print(f"    Time saved: {time_saved:.2f}s")

        print("✅ Parallel execution test passed")
        return True

    except Exception as e:
        print(f"❌ Parallel execution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_unified_registry():
    """Test the unified workflow registry system."""
    print("\n🧪 Testing unified workflow registry...")

    try:
        config = WorkflowConfig(batch_size=5, seed=666)

        # Test creating workflows through unified registry
        people_workflow = UnifiedWorkflowRegistry.create_workflow(
            "people", config, DatabaseConfig.for_testing()
        )
        assert isinstance(
            people_workflow, PeopleWorkflow
        ), "Should create PeopleWorkflow"

        companies_workflow = UnifiedWorkflowRegistry.create_workflow(
            "companies", config, DatabaseConfig.for_testing()
        )
        assert isinstance(
            companies_workflow, CompaniesWorkflow
        ), "Should create CompaniesWorkflow"

        # Test creating dataset workflow
        dataset_workflow = UnifiedWorkflowRegistry.create_workflow(
            "dataset", config, DatabaseConfig.for_testing()
        )
        assert isinstance(
            dataset_workflow, DatasetWorkflow
        ), "Should create DatasetWorkflow"

        # Test error handling for unknown workflow
        try:
            UnifiedWorkflowRegistry.create_workflow("nonexistent", config)
            assert False, "Should raise error for unknown workflow"
        except ValueError as e:
            assert "Unknown workflow" in str(e), "Should mention unknown workflow"

        print("✅ Unified workflow registry test passed")
        return True

    except Exception as e:
        print(f"❌ Unified workflow registry test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with old workflow interfaces."""
    print("\n🧪 Testing backward compatibility...")

    try:
        config = WorkflowConfig(batch_size=5, seed=777, write_mode="truncate")

        # Test old-style workflow creation still works
        old_people_workflow = PeopleWorkflow(config, DatabaseConfig.for_testing())
        old_companies_workflow = CompaniesWorkflow(config, DatabaseConfig.for_testing())

        # Test they still have the same interface
        assert old_people_workflow.workflow_name == "People Generation"
        assert old_companies_workflow.workflow_name == "Companies Generation"

        # Test batch generation still works
        people_batch = old_people_workflow.generate_batch(3)
        companies_batch = old_companies_workflow.generate_batch(2)

        assert len(people_batch) == 3, "Should generate 3 people"
        assert len(companies_batch) == 2, "Should generate 2 companies"

        # Test execution still works
        people_result = old_people_workflow.execute(10)
        companies_result = old_companies_workflow.execute(5)

        assert people_result.success, "People workflow should succeed"
        assert companies_result.success, "Companies workflow should succeed"

        # Test old factory functions still work
        new_people_workflow = create_workflow_from_name(
            "people", config, DatabaseConfig.for_testing()
        )
        assert new_people_workflow is not None, "Should create workflow from name"

        print("✅ Backward compatibility test passed")
        return True

    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_error_handling_and_recovery():
    """Test error handling and recovery mechanisms."""
    print("\n🧪 Testing error handling and recovery...")

    try:
        # Test invalid entity type
        config = WorkflowConfig(batch_size=5, seed=888)

        try:
            create_entity_workflow("invalid_entity", config)
            assert False, "Should raise error for invalid entity type"
        except ValueError as e:
            assert "invalid_entity" in str(e), "Should mention invalid entity type"

        # Test invalid dataset spec
        invalid_spec = DatasetSpec(
            workflows={"people": -10}, description="Invalid spec"  # Negative count
        )

        try:
            invalid_spec.validate()
            assert False, "Should raise error for negative count"
        except ValueError as e:
            assert "positive" in str(e), "Should mention positive count requirement"

        # Test workflow step failure handling
        step = WorkflowStep("test_workflow", 10)
        assert step.status == WorkflowStepStatus.PENDING, "Should start as pending"

        step.mark_ready()
        assert step.status == WorkflowStepStatus.READY, "Should be ready"

        step.mark_running()
        assert step.status == WorkflowStepStatus.RUNNING, "Should be running"
        assert step.start_time is not None, "Should have start time"

        step.mark_failed("Test error")
        assert step.status == WorkflowStepStatus.FAILED, "Should be failed"
        assert step.error_message == "Test error", "Should have error message"
        assert step.end_time is not None, "Should have end time"

        print("✅ Error handling and recovery test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling and recovery test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def display_enhanced_sample_data():
    """Display sample data using the new enhanced system."""
    print("\n📊 Enhanced Sample Data Generation:")

    try:
        # Show quick generation
        print("\n🚀 Quick Generation (No Database):")
        quick_people = quick_generate_people(2, seed=999)
        quick_companies = quick_generate_companies(2, seed=999)

        print("  👥 Quick People Sample:")
        for i, person in enumerate(quick_people, 1):
            print(f"    {i}. {person['full_name']} ({person['age']} years)")
            print(f"       {person['job_title']} - ${person['annual_income']:,}/year")

        print("  🏢 Quick Companies Sample:")
        for i, company in enumerate(quick_companies, 1):
            print(f"    {i}. {company['company_name']}")
            print(
                f"       {company['industry']} - {company['employee_count']:,} employees"
            )

        # Show template-based generation
        print("\n📋 Template-Based Dataset (small_demo):")
        dataset = quick_generate_dataset("small_demo", seed=999)

        print(
            f"  Total entities: {sum(len(entities) for entities in dataset.values())}"
        )
        for entity_type, entities in dataset.items():
            print(f"  • {entity_type}: {len(entities)} records")

        # Show orchestrator summary
        print("\n🎛️  Orchestrator Capabilities:")
        config = WorkflowConfig(batch_size=10, seed=999)
        spec = DatasetSpec(
            workflows={"companies": 5, "people": 15},
            dependencies={"people": ["companies"]},
            description="Demo dataset with dependencies",
        )

        orchestrator = DatasetOrchestrator(spec, config, DatabaseConfig.for_testing())
        execution_order = orchestrator.execution_groups

        print(f"  Execution groups: {len(execution_order)}")
        for i, group in enumerate(execution_order, 1):
            print(f"    Group {i}: {', '.join(group)}")

        # Show system info
        print("\n🔧 System Configuration:")
        from workflows import get_system_info

        info = get_system_info()
        print(f"  Version: {info['version']}")
        print(f"  Available workflows: {', '.join(info['available_workflows'])}")
        print(f"  Available templates: {', '.join(info['available_templates'])}")

    except Exception as e:
        print(f"❌ Error displaying sample data: {e}")
        import traceback

        traceback.print_exc()


def test_legacy_compatibility():
    """Test that legacy person generation still works."""
    print("\n🧪 Testing legacy compatibility...")

    try:
        # Test original person generation function
        persons = generate_multiple_persons(3, seed=42)

        assert len(persons) == 3, "Should generate 3 persons"

        for person in persons:
            assert person.full_name, "Person should have a name"
            assert person.age >= 18, "Person should be adult"
            assert person.person_id, "Person should have ID"
            assert person.job_title, "Person should have job title"

        print("✅ Legacy compatibility test passed")
        return True

    except Exception as e:
        print(f"❌ Legacy compatibility test failed: {e}")
        import traceback

        traceback.print_exc()
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
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests for the enhanced workflow system."""
    print("🌍 Earth Enhanced Workflow System Tests")
    print("=" * 60)

    tests = [
        test_database_operations,
        test_legacy_compatibility,
        test_new_dataset_orchestrator,
        test_dataset_workflow_wrapper,
        test_template_system,
        test_validation_system,
        test_quick_generation_functions,
        test_enhanced_entity_workflows,
        test_parallel_execution,
        test_unified_registry,
        test_backward_compatibility,
        test_error_handling_and_recovery,
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
            import traceback

            traceback.print_exc()
            failed += 1

    # Show enhanced sample data
    display_enhanced_sample_data()

    # Show system summary
    print("\n" + "=" * 60)
    try:
        print_system_summary()
    except Exception as e:
        print(f"Error displaying system summary: {e}")

    # Final results
    print(f"\n📈 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {passed + failed}")

    if failed == 0:
        print(f"\n🎉 All tests passed! Enhanced Earth workflow system is ready!")
        print(f"\n🚀 Key Features Verified:")
        print(f"  • Dataset orchestration with dependency management")
        print(f"  • Parallel workflow execution")
        print(f"  • Template-based dataset generation")
        print(f"  • Enhanced validation and error handling")
        print(f"  • Backward compatibility with legacy workflows")
        print(f"  • Quick generation functions for rapid prototyping")
        print(f"  • Comprehensive statistics and monitoring")

        return True
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
