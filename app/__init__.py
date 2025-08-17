"""
Earth Data Generator Application

This package provides the main application interface for the Earth synthetic data generator.
It includes CLI interfaces, workflow orchestration, and high-level data generation functions.

The application is built on top of the core Earth package and provides:
- Interactive command-line interface
- Unified workflow system for different data types
- Dataset orchestration with dependency management
- Comprehensive progress tracking and statistics
"""

from typing import Dict, Any, List, Optional

# Import workflow system
from .workflows import (
    # Core workflow classes
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    # Unified workflow system
    EntityWorkflow,
    PeopleWorkflow,
    CompaniesWorkflow,
    UnifiedWorkflowRegistry,
    # Dataset orchestration
    DatasetOrchestrator,
    DatasetSpec,
    DatasetWorkflow,
    # High-level functions
    create_workflow_from_name,
    get_workflow_info,
    list_available_workflows,
    get_system_info,
    print_system_summary,
    # Quick generation functions
    quick_generate_people,
    quick_generate_companies,
    quick_generate_dataset,
    # Configuration and templates
    AVAILABLE_WORKFLOWS,
    WORKFLOW_CONFIGS,
    DATASET_TEMPLATES,
)

# Import CLI interface
from .main import EarthCLI, main

__all__ = [
    # CLI Interface
    "EarthCLI",
    "main",
    # Workflow System
    "BaseWorkflow",
    "WorkflowConfig",
    "WorkflowResult",
    "WorkflowStatus",
    "EntityWorkflow",
    "PeopleWorkflow",
    "CompaniesWorkflow",
    "UnifiedWorkflowRegistry",
    # Dataset Orchestration
    "DatasetOrchestrator",
    "DatasetSpec",
    "DatasetWorkflow",
    # High-level Functions
    "create_workflow_from_name",
    "get_workflow_info",
    "list_available_workflows",
    "get_system_info",
    "print_system_summary",
    # Quick Generation
    "quick_generate_people",
    "quick_generate_companies",
    "quick_generate_dataset",
    # Configuration
    "AVAILABLE_WORKFLOWS",
    "WORKFLOW_CONFIGS",
    "DATASET_TEMPLATES",
    # Convenience Functions
    "generate_sample_data",
    "generate_custom_dataset",
    "list_workflow_capabilities",
]

# Application metadata
__version__ = "0.3.0"
__title__ = "Earth Data Generator Application"
__description__ = "Interactive CLI and workflow system for generating synthetic data"


def generate_sample_data(
    entity_type: str = "person", count: int = 10, seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Generate sample data for testing and exploration.

    Args:
        entity_type: Type of entity to generate ("person" or "company")
        count: Number of records to generate
        seed: Random seed for reproducible results

    Returns:
        List of generated records

    Example:
        >>> from app import generate_sample_data
        >>> people = generate_sample_data("person", 5)
        >>> companies = generate_sample_data("company", 3)
    """
    if entity_type.lower() == "person":
        return quick_generate_people(count, seed)
    elif entity_type.lower() == "company":
        return quick_generate_companies(count, seed)
    else:
        raise ValueError(
            f"Unknown entity type: {entity_type}. Use 'person' or 'company'"
        )


def generate_custom_dataset(
    people_count: int = 100,
    companies_count: int = 10,
    template_name: Optional[str] = None,
    seed: Optional[int] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a custom dataset with specified counts.

    Args:
        people_count: Number of people to generate
        companies_count: Number of companies to generate
        template_name: Use predefined template instead of custom counts
        seed: Random seed for reproducible results

    Returns:
        Dictionary with 'person' and 'company' keys containing lists of records

    Example:
        >>> from app import generate_custom_dataset
        >>> dataset = generate_custom_dataset(people_count=50, companies_count=5)
        >>> print(f"Generated {len(dataset['person'])} people and {len(dataset['company'])} companies")
    """
    if template_name:
        return quick_generate_dataset(template_name, seed)
    else:
        # Create temporary template
        temp_template = {
            "people_count": people_count,
            "companies_count": companies_count,
        }

        # Generate using quick functions
        result = {}

        from earth.generators.base import GeneratorConfig
        from earth.generators.factory import create_generator

        config = GeneratorConfig(seed=seed)

        # Generate companies
        company_generator = create_generator("company", config)
        result["company"] = company_generator.generate_batch_dicts(companies_count)

        # Generate people
        person_generator = create_generator("person", config)
        result["person"] = person_generator.generate_batch_dicts(people_count)

        return result


def list_workflow_capabilities() -> Dict[str, Any]:
    """
    Get comprehensive information about workflow capabilities.

    Returns:
        Dictionary with detailed workflow information

    Example:
        >>> from app import list_workflow_capabilities
        >>> capabilities = list_workflow_capabilities()
        >>> print(f"Available workflows: {capabilities['workflows']}")
    """
    system_info = get_system_info()

    return {
        "version": __version__,
        "workflows": list(AVAILABLE_WORKFLOWS.keys()),
        "templates": list(DATASET_TEMPLATES.keys()),
        "entity_types": ["person", "company"],
        "features": {
            "unified_workflows": True,
            "dataset_orchestration": True,
            "dependency_management": True,
            "parallel_execution": True,
            "comprehensive_statistics": True,
            "database_persistence": True,
            "in_memory_generation": True,
        },
        "workflow_details": {
            name: {
                "description": AVAILABLE_WORKFLOWS[name]["description"],
                "default_count": AVAILABLE_WORKFLOWS[name].get("default_count"),
                "config": WORKFLOW_CONFIGS.get(name, {}),
            }
            for name in AVAILABLE_WORKFLOWS.keys()
        },
        "template_details": DATASET_TEMPLATES,
    }


def run_cli():
    """
    Convenience function to run the CLI interface.

    Example:
        >>> from app import run_cli
        >>> run_cli()  # Starts interactive CLI
    """
    main()


# Module-level convenience functions for interactive use
def info():
    """Print system information and capabilities."""
    print_system_summary()


def workflows():
    """List available workflows."""
    print("\nAvailable Workflows:")
    for name, info in AVAILABLE_WORKFLOWS.items():
        print(f"  • {name}: {info['description']}")
        if info.get("default_count"):
            print(f"    Default: {info['default_count']:,} records")


def templates():
    """List available dataset templates."""
    print("\nDataset Templates:")
    for name, info in DATASET_TEMPLATES.items():
        print(f"  • {name}: {info['description']}")
        print(
            f"    People: {info['workflows']['people']:,}, Companies: {info['workflows']['companies']:,}"
        )


# Development and testing helpers
def _validate_installation():
    """Validate that the Earth application is properly installed and configured."""
    try:
        # Test core imports
        from earth.core.loader import DatabaseConfig
        from earth.generators.factory import create_generator

        # Test workflow creation
        config = WorkflowConfig(batch_size=10)
        workflow = create_workflow_from_name("people", config)

        # Test quick generation
        sample_data = quick_generate_people(count=1)

        return {
            "status": "valid",
            "message": "Earth application is properly installed and configured",
            "core_available": True,
            "generators_available": True,
            "workflows_available": True,
            "sample_generation": len(sample_data) > 0,
        }

    except Exception as e:
        return {
            "status": "invalid",
            "message": f"Installation validation failed: {e}",
            "error": str(e),
        }


if __name__ == "__main__":
    # When app module is run directly, start the CLI
    run_cli()
