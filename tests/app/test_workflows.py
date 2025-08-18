#!/usr/bin/env python3
"""
Tests for the workflow system in app/workflows.
Tests orchestration, templates, and workflow execution.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "app"))

try:
    from earth.core.loader import DatabaseConfig
    from workflows import (
        WorkflowConfig,
        DatasetSpec,
        PeopleWorkflow,
        CompaniesWorkflow,
        DatasetWorkflow,
        list_dataset_templates,
        create_workflow_from_name,
        create_entity_workflow,
        create_dataset_workflow,
        UnifiedWorkflowRegistry,
        get_template_info,
        validate_dataset_spec,
        quick_generate_people,
        quick_generate_companies,
        quick_generate_dataset,
    )
    from workflows.dataset_orchestrator import (
        DatasetOrchestrator,
        WorkflowStep,
        WorkflowStepStatus,
    )
except ImportError as e:
    print(f"❌ Import error in test_workflows: {e}")
    sys.exit(1)


def test_workflow_config():
    """Test WorkflowConfig creation and validation."""
    print("🧪 Testing workflow configuration...")

    try:
        # Test default config
        config = WorkflowConfig()
        assert config.batch_size > 0, "Should have positive batch size"
        assert config.write_mode in [
            "truncate",
            "append",
        ], "Should have valid write mode"

        # Test custom config
        custom_config = WorkflowConfig(batch_size=100, seed=42, write_mode="truncate")
        assert custom_config.batch_size == 100, "Should use custom batch size"
        assert custom_config.seed == 42, "Should use custom seed"
        assert custom_config.write_mode == "truncate", "Should use custom write mode"

        print("✅ Workflow configuration tests passed")
        return True

    except Exception as e:
        print(f"❌ Workflow configuration test failed: {e}")
        return False


def test_dataset_spec():
    """Test DatasetSpec creation and validation."""
    print("🧪 Testing dataset specification...")

    try:
        # Test simple spec
        spec = DatasetSpec(
            workflows={"people": 100, "companies": 10}, description="Test dataset"
        )

        assert spec.workflows["people"] == 100, "Should have correct people count"
        assert spec.workflows["companies"] == 10, "Should have correct company count"
        assert spec.description == "Test dataset", "Should have correct description"

        # Test spec with dependencies
        dep_spec = DatasetSpec(
            workflows={"companies": 5, "people": 25},
            dependencies={"people": ["companies"]},
            description="Dataset with dependencies",
        )

        dep_spec.validate()
        execution_order = dep_spec.get_execution_order()

        assert len(execution_order) == 2, "Should have 2 execution groups"
        assert "companies" in execution_order[0], "Companies should be in first group"
        assert "people" in execution_order[1], "People should depend on companies"

        print("✅ Dataset specification tests passed")
        return True

    except Exception as e:
        print(f"❌ Dataset specification test failed: {e}")
        return False


def test_people_workflow():
    """Test PeopleWorkflow functionality."""
    print("🧪 Testing people workflow...")

    try:
        config = WorkflowConfig(batch_size=5, seed=123, write_mode="truncate")
        workflow = PeopleWorkflow(config, DatabaseConfig.for_testing())

        # Test workflow properties
        assert workflow.workflow_name == "People Generation", "Should have correct name"
        assert workflow.schema_name == "raw", "Should target raw schema"
        assert workflow.table_name == "persons", "Should target persons table"

        # Test batch generation
        batch_data = workflow.generate_batch(3)
        assert len(batch_data) == 3, "Should generate 3 person records"
        assert "full_name" in batch_data[0], "Should have full_name field"
        assert "age" in batch_data[0], "Should have age field"

        # Test statistics
        stats = workflow.get_generation_statistics(batch_data)
        assert stats["entity_type"] == "person", "Should have correct entity type"
        assert stats["batch_size"] == 3, "Should have correct batch size"
        assert "person_stats" in stats, "Should have person-specific stats"

        # Test execution
        result = workflow.execute(10)
        assert result.success, f"Should execute successfully: {result.error_message}"
        assert result.records_generated == 10, "Should generate 10 records"
        assert result.execution_time > 0, "Should have positive execution time"

        print("✅ People workflow tests passed")
        return True

    except Exception as e:
        print(f"❌ People workflow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_companies_workflow():
    """Test CompaniesWorkflow functionality."""
    print("🧪 Testing companies workflow...")

    try:
        config = WorkflowConfig(batch_size=3, seed=456, write_mode="truncate")
        workflow = CompaniesWorkflow(config, DatabaseConfig.for_testing())

        # Test workflow properties
        assert (
            workflow.workflow_name == "Companies Generation"
        ), "Should have correct name"
        assert workflow.schema_name == "raw", "Should target raw schema"
        assert workflow.table_name == "companies", "Should target companies table"

        # Test batch generation
        batch_data = workflow.generate_batch(2)
        assert len(batch_data) == 2, "Should generate 2 company records"
        assert "company_name" in batch_data[0], "Should have company_name field"
        assert "industry" in batch_data[0], "Should have industry field"

        # Test statistics
        stats = workflow.get_generation_statistics(batch_data)
        assert stats["entity_type"] == "company", "Should have correct entity type"
        assert stats["batch_size"] == 2, "Should have correct batch size"
        assert "company_stats" in stats, "Should have company-specific stats"

        # Test execution
        result = workflow.execute(5)
        assert result.success, f"Should execute successfully: {result.error_message}"
        assert result.records_generated == 5, "Should generate 5 records"

        print("✅ Companies workflow tests passed")
        return True

    except Exception as e:
        print(f"❌ Companies workflow test failed: {e}")
        return False


def test_dataset_orchestrator():
    """Test the dataset orchestration system."""
    print("🧪 Testing dataset orchestrator...")

    try:
        # Create dataset spec with dependencies
        spec = DatasetSpec(
            workflows={"companies": 5, "people": 15},
            dependencies={"people": ["companies"]},
            description="Test orchestration dataset",
        )

        config = WorkflowConfig(batch_size=3, seed=789, write_mode="truncate")
        orchestrator = DatasetOrchestrator(
            spec, config, DatabaseConfig.for_testing(), max_parallel_workflows=2
        )

        # Test orchestrator properties
        assert len(orchestrator.workflow_steps) == 2, "Should have 2 workflow steps"
        assert "companies" in orchestrator.workflow_steps, "Should have companies step"
        assert "people" in orchestrator.workflow_steps, "Should have people step"

        # Test execution order calculation
        execution_groups = orchestrator.execution_groups
        assert len(execution_groups) == 2, "Should have 2 execution groups"
        assert "companies" in execution_groups[0], "Companies should be first"
        assert "people" in execution_groups[1], "People should be second"

        # Test execution (sequential for testing)
        summary = orchestrator.execute(use_parallel=False)

        assert (
            summary["execution_summary"]["overall_status"] == "completed"
        ), "Should complete successfully"
        assert (
            summary["execution_summary"]["total_records_generated"] >= 20
        ), "Should generate at least 20 records"
        assert (
            summary["performance_metrics"]["workflows_completed"] == 2
        ), "Should complete 2 workflows"
        assert (
            summary["performance_metrics"]["workflows_failed"] == 0
        ), "Should have no failures"

        print("✅ Dataset orchestrator tests passed")
        return True

    except Exception as e:
        print(f"❌ Dataset orchestrator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_template_system():
    """Test the dataset template system."""
    print("🧪 Testing template system...")

    try:
        # Test listing templates
        templates = list_dataset_templates()
        assert len(templates) >= 3, "Should have at least 3 templates"
        assert "small_demo" in templates, "Should have small_demo template"
        assert "medium_dev" in templates, "Should have medium_dev template"

        # Test getting template info
        template_info = get_template_info("small_demo")
        assert "description" in template_info, "Should have description"
        assert "workflows" in template_info, "Should have workflows"
        assert "people" in template_info["workflows"], "Should include people workflow"

        # Test creating workflow from template
        config = WorkflowConfig(batch_size=5, seed=111, write_mode="truncate")
        dataset_workflow = create_dataset_workflow(
            template_name="small_demo",
            config=config,
            db_config=DatabaseConfig.for_testing(),
        )

        assert dataset_workflow is not None, "Should create workflow from template"

        # Test template execution
        result = dataset_workflow.execute()
        assert (
            result.success
        ), f"Template workflow should succeed: {result.error_message}"
        assert result.records_generated > 0, "Should generate records"

        print("✅ Template system tests passed")
        return True

    except Exception as e:
        print(f"❌ Template system test failed: {e}")
        return False


def test_quick_generation_functions():
    """Test quick generation convenience functions."""
    print("🧪 Testing quick generation functions...")

    try:
        # Test quick people generation
        people_data = quick_generate_people(3, seed=222)
        assert len(people_data) == 3, "Should generate 3 people"
        assert "full_name" in people_data[0], "Should have full_name field"
        assert "age" in people_data[0], "Should have age field"

        # Test quick companies generation
        companies_data = quick_generate_companies(2, seed=333)
        assert len(companies_data) == 2, "Should generate 2 companies"
        assert "company_name" in companies_data[0], "Should have company_name field"
        assert "industry" in companies_data[0], "Should have industry field"

        # Test quick dataset generation
        dataset = quick_generate_dataset("small_demo", seed=444)
        assert "person" in dataset, "Should have person data"
        assert "company" in dataset, "Should have company data"
        assert len(dataset["person"]) > 0, "Should have person records"
        assert len(dataset["company"]) > 0, "Should have company records"

        print("✅ Quick generation functions tests passed")
        return True

    except Exception as e:
        print(f"❌ Quick generation functions test failed: {e}")
        return False


def test_unified_workflow_registry():
    """Test the unified workflow registry."""
    print("🧪 Testing unified workflow registry...")

    try:
        config = WorkflowConfig(batch_size=3, seed=555)

        # Test creating people workflow
        people_workflow = UnifiedWorkflowRegistry.create_workflow(
            "people", config, DatabaseConfig.for_testing()
        )
        assert isinstance(
            people_workflow, PeopleWorkflow
        ), "Should create PeopleWorkflow"

        # Test creating companies workflow
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

        print("✅ Unified workflow registry tests passed")
        return True

    except Exception as e:
        print(f"❌ Unified workflow registry test failed: {e}")
        return False


def test_validation_system():
    """Test the validation system."""
    print("🧪 Testing validation system...")

    try:
        # Test valid dataset spec
        valid_spec = DatasetSpec(
            workflows={"people": 50, "companies": 5},
            dependencies={"people": ["companies"]},
            description="Valid test dataset",
        )

        errors = validate_dataset_spec(valid_spec)
        assert len(errors) == 0, f"Valid spec should have no errors: {errors}"

        # Test invalid workflow reference
        invalid_spec = DatasetSpec(
            workflows={"nonexistent": 10, "people": 50},
            description="Invalid workflow reference",
        )

        errors = validate_dataset_spec(invalid_spec)
        assert len(errors) > 0, "Should have errors for unknown workflow"
        assert any(
            "nonexistent" in error for error in errors
        ), "Should mention unknown workflow"

        # Test negative count validation
        negative_spec = DatasetSpec(
            workflows={"people": -10}, description="Negative count test"
        )

        try:
            negative_spec.validate()
            assert False, "Should raise error for negative count"
        except ValueError as e:
            assert "positive" in str(e), "Should mention positive count requirement"

        print("✅ Validation system tests passed")
        return True

    except Exception as e:
        print(f"❌ Validation system test failed: {e}")
        return False


def test_workflow_step_lifecycle():
    """Test workflow step status lifecycle."""
    print("🧪 Testing workflow step lifecycle...")

    try:
        step = WorkflowStep("test_workflow", 10)

        # Test initial state
        assert step.status == WorkflowStepStatus.PENDING, "Should start as pending"
        assert step.start_time is None, "Should not have start time"
        assert step.end_time is None, "Should not have end time"

        # Test ready state
        step.mark_ready()
        assert step.status == WorkflowStepStatus.READY, "Should be ready"

        # Test running state
        step.mark_running()
        assert step.status == WorkflowStepStatus.RUNNING, "Should be running"
        assert step.start_time is not None, "Should have start time"

        # Test completed state
        step.mark_completed(10)
        assert step.status == WorkflowStepStatus.COMPLETED, "Should be completed"
        assert step.end_time is not None, "Should have end time"
        assert step.target_records == 10, "Should have correct record count"

        # Test execution time calculation
        execution_time = step.duration
        assert execution_time >= 0, "Should have non-negative execution time"

        # Test failed state
        failed_step = WorkflowStep("failed_workflow", 5)
        failed_step.mark_running()
        failed_step.mark_failed("Test error")

        assert failed_step.status == WorkflowStepStatus.FAILED, "Should be failed"
        assert failed_step.error_message == "Test error", "Should have error message"

        print("✅ Workflow step lifecycle tests passed")
        return True

    except Exception as e:
        print(f"❌ Workflow step lifecycle test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with old interfaces."""
    print("🧪 Testing backward compatibility...")

    try:
        config = WorkflowConfig(batch_size=5, seed=777, write_mode="truncate")

        # Test old-style workflow creation still works
        old_people_workflow = PeopleWorkflow(config, DatabaseConfig.for_testing())
        old_companies_workflow = CompaniesWorkflow(config, DatabaseConfig.for_testing())

        # Test they have expected interface
        assert old_people_workflow.workflow_name == "People Generation"
        assert old_companies_workflow.workflow_name == "Companies Generation"

        # Test old factory functions still work
        new_people_workflow = create_workflow_from_name(
            "people", config, DatabaseConfig.for_testing()
        )
        assert new_people_workflow is not None, "Should create workflow from name"

        # Test entity workflow creation
        entity_workflow = create_entity_workflow(
            "person", config, DatabaseConfig.for_testing()
        )
        assert entity_workflow is not None, "Should create entity workflow"

        print("✅ Backward compatibility tests passed")
        return True

    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False


def display_workflow_sample():
    """Display sample workflow execution."""
    print("\n🔄 Sample Workflow Execution:")
    print("-" * 60)

    try:
        # Show quick generation
        print("\n🚀 Quick Generation Sample:")
        people = quick_generate_people(2, seed=999)
        companies = quick_generate_companies(1, seed=999)

        print("  👥 People:")
        for person in people:
            print(
                f"    • {person['full_name']} ({person['age']}) - {person['job_title']}"
            )

        print("  🏢 Companies:")
        for company in companies:
            print(f"    • {company['company_name']} - {company['industry']}")

        # Show template info
        print("\n📋 Available Templates:")
        templates = list_dataset_templates()
        for template in templates:
            info = get_template_info(template)
            print(f"  • {template}: {info.get('description', 'No description')}")

    except Exception as e:
        print(f"❌ Error displaying workflow sample: {e}")


def main():
    """Run all workflow tests."""
    print("🔄 Workflow System Tests")
    print("=" * 50)

    tests = [
        test_workflow_config,
        test_dataset_spec,
        test_people_workflow,
        test_companies_workflow,
        test_dataset_orchestrator,
        test_template_system,
        test_quick_generation_functions,
        test_unified_workflow_registry,
        test_validation_system,
        test_workflow_step_lifecycle,
        test_backward_compatibility,
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

    # Display sample workflow execution
    display_workflow_sample()

    print(f"\n📊 Workflow Tests - Passed: {passed}, Failed: {failed}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
