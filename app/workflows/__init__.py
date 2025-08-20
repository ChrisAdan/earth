"""
Workflows package for Earth data generation.

This package contains all workflow implementations for generating
different types of synthetic data entities using a unified, DRY approach.
"""

from typing import Dict, Any, Optional, List

# Core workflow infrastructure
from .base import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    WorkflowRegistry,
    register_workflow,
)

# Unified workflow components
from .unified_workflow import (
    EntityWorkflow,
    PeopleWorkflow,
    CompaniesWorkflow,
    create_entity_workflow,
    UnifiedWorkflowRegistry,
)

# Constant configs
from .config import (
    AVAILABLE_WORKFLOWS,
    WORKFLOW_CONFIGS,
    DATASET_TEMPLATES,
)

# Dataset orchestration
from .dataset_orchestrator import (
    DatasetOrchestrator,
    DatasetSpec,
    WorkflowStep,
    DatasetWorkflow,
)

from earth import __version__

# Generator system imports
from earth.generators.base import (
    BaseGenerator,
    GeneratorConfig,
)
from earth.generators.factory import (
    create_generator,
)

# Auto-register workflows when package is imported
# This ensures all workflows are available in the registry

__all__ = [
    # Base classes
    "BaseWorkflow",
    "WorkflowConfig",
    "WorkflowResult",
    "WorkflowStatus",
    "WorkflowRegistry",
    "register_workflow",
    # Unified workflow system
    "EntityWorkflow",
    "PeopleWorkflow",
    "CompaniesWorkflow",
    "create_entity_workflow",
    "UnifiedWorkflowRegistry",
    # Dataset orchestration
    "DatasetOrchestrator",
    "DatasetSpec",
    "WorkflowStep",
    "DatasetWorkflow",
    # Generator system
    "BaseGenerator",
    "GeneratorConfig",
    "create_generator",
    # High-level functions
    "get_workflow_info",
    "list_available_workflows",
    "create_workflow_from_name",
    "get_system_info",
    "print_system_summary",
    "AVAILABLE_WORKFLOWS",
    "WORKFLOW_CONFIGS",
    "DATASET_TEMPLATES",
]


def get_workflow_info(workflow_name: str) -> dict:
    """
    Get information about a specific workflow.

    Args:
        workflow_name: Name of the workflow

    Returns:
        Dictionary with workflow information

    Raises:
        ValueError: If workflow not found
    """
    if workflow_name not in WORKFLOW_CONFIGS:
        available = list(WORKFLOW_CONFIGS.keys())
        raise ValueError(f"Unknown workflow '{workflow_name}'. Available: {available}")

    return WORKFLOW_CONFIGS[workflow_name].copy()


def list_available_workflows() -> List[str]:
    """Get list of all available workflow names."""
    return list(WORKFLOW_CONFIGS.keys())


def list_dataset_templates() -> List[str]:
    """Get list of all available dataset templates."""
    return list(DATASET_TEMPLATES.keys())


def create_workflow_from_name(
    workflow_name: str, config: WorkflowConfig, db_config=None, **kwargs
) -> BaseWorkflow:
    """
    Factory function to create workflow instances by name.

    Args:
        workflow_name: Name of workflow to create
        config: Workflow configuration
        db_config: Database configuration (optional)
        **kwargs: Additional workflow-specific arguments

    Returns:
        Workflow instance

    Raises:
        ValueError: If workflow name not recognized
    """
    if workflow_name == "full_dataset":
        # Special handling for full dataset workflow
        dataset_spec = kwargs.get("dataset_spec")
        if not dataset_spec:
            raise ValueError("full_dataset workflow requires dataset_spec parameter")

        return DatasetWorkflow(config, db_config, dataset_spec=dataset_spec)

    return UnifiedWorkflowRegistry.create_workflow(
        workflow_name, config, db_config, **kwargs
    )


def create_dataset_workflow(
    template_name: Optional[str] = None,
    custom_spec: Optional[DatasetSpec] = None,
    config: Optional[WorkflowConfig] = None,
    db_config=None,
    **kwargs,
) -> DatasetWorkflow:
    """
    Create a dataset workflow from template or custom specification.

    Args:
        template_name: Name of predefined template
        custom_spec: Custom dataset specification
        config: Base workflow configuration
        db_config: Database configuration
        **kwargs: Additional arguments

    Returns:
        DatasetWorkflow instance

    Raises:
        ValueError: If neither template nor spec provided
    """
    if template_name and custom_spec:
        raise ValueError("Provide either template_name or custom_spec, not both")

    if not template_name and not custom_spec:
        raise ValueError("Must provide either template_name or custom_spec")

    # Use default config if none provided
    if config is None:
        config = WorkflowConfig()

    # Create spec from template if needed
    if template_name:
        if template_name not in DATASET_TEMPLATES:
            available = list(DATASET_TEMPLATES.keys())
            raise ValueError(
                f"Unknown template '{template_name}'. Available: {available}"
            )

        template = DATASET_TEMPLATES[template_name]
        custom_spec = DatasetSpec(
            workflows=template["workflows"],
        )

    return DatasetWorkflow(config, db_config, custom_spec, **kwargs)


def get_template_info(template_name: str) -> dict:
    """
    Get information about a dataset template.

    Args:
        template_name: Name of the template

    Returns:
        Dictionary with template information

    Raises:
        ValueError: If template not found
    """
    if template_name not in DATASET_TEMPLATES:
        available = list(DATASET_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")

    return DATASET_TEMPLATES[template_name].copy()


def validate_dataset_spec(spec: DatasetSpec) -> List[str]:
    """
    Validate a dataset specification.

    Args:
        spec: Dataset specification to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    try:
        spec.validate()
    except ValueError as e:
        errors.append(str(e))

    return errors


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the workflow system.

    Returns:
        Dictionary with system information
    """
    return {
        "version": __version__,
        "available_workflows": list(WORKFLOW_CONFIGS.keys()),
        "available_templates": list(DATASET_TEMPLATES.keys()),
        "workflow_configs": WORKFLOW_CONFIGS,
        "dataset_templates": DATASET_TEMPLATES,
        "unified_system": True,
    }


def print_system_summary():
    """Print a summary of the available workflows and templates."""
    info = get_system_info()

    print(f"Earth Workflows System v{info['version']}")
    print("=" * 50)

    print(f"\nAvailable Workflows ({len(info['available_workflows'])}):")
    for workflow in info["available_workflows"]:
        details = info["workflow_configs"][workflow]
        print(f"  • {workflow}: {details['description']}")
        if details.get("default_count"):
            print(f"    Default: {details['default_count']} records")
        print(f"    Table: {details['schema']}.{details['table']}")

    print(f"\nDataset Templates ({len(info['available_templates'])}):")
    for template in info["available_templates"]:
        details = info["dataset_templates"][template]
        print(f"  • {template}: {details['description']}")
        print(
            f"    People: {details['workflows']['people']:,}, Companies: {details['workflows']['companies']:,}"
        )

    print(f"\nSystem Features:")
    print(f"  • Unified entity workflow interface")
    print(f"  • Template-based dataset generation")
    print(f"  • Dependency-aware orchestration")
    print(f"  • Configurable batch processing")
    print(f"  • Comprehensive validation and statistics")


# Convenience functions for quick data generation
def quick_generate_people(
    count: int = 100, seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Quick function to generate people data without database storage.

    Args:
        count: Number of people to generate
        seed: Random seed for reproducible results

    Returns:
        List of person dictionaries
    """
    config = GeneratorConfig(seed=seed)
    generator = create_generator("person", config)
    return generator.generate_batch_dicts(count)


def quick_generate_companies(
    count: int = 10, seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Quick function to generate company data without database storage.

    Args:
        count: Number of companies to generate
        seed: Random seed for reproducible results

    Returns:
        List of company dictionaries
    """
    config = GeneratorConfig(seed=seed)
    generator = create_generator("company", config)
    return generator.generate_batch_dicts(count)


def quick_generate_dataset(
    template: str = "small_demo", seed: Optional[int] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Quick function to generate a complete dataset without database storage.

    Args:
        template: Dataset template to use
        seed: Random seed for reproducible results

    Returns:
        Dictionary with entity types as keys and lists of records as values
    """
    if template not in DATASET_TEMPLATES:
        raise ValueError(f"Unknown template: {template}")

    template_info = DATASET_TEMPLATES[template]
    result = {}

    # Generate companies first
    config = GeneratorConfig(seed=seed)
    company_generator = create_generator("company", config)
    result["company"] = company_generator.generate_batch_dicts(
        template_info["workflows"]["companies"]
    )

    # Generate people
    person_generator = create_generator("person", config)
    result["person"] = person_generator.generate_batch_dicts(
        template_info["workflows"]["people"]
    )

    return result
