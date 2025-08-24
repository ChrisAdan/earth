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
    "create_dataset_workflow",
    "get_system_info",
    "print_system_summary",
    "quick_generate_full_dataset",
    # Constants
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
            # If no dataset_spec provided, create a default one
            # This handles the case where CLI doesn't pass dataset_spec correctly
            from .dataset_orchestrator import DatasetSpec

            dataset_spec = DatasetSpec.for_full_dataset()

        if not isinstance(dataset_spec, DatasetSpec):
            raise ValueError(
                f"full_dataset workflow requires DatasetSpec instance, got {type(dataset_spec)}"
            )

        return DatasetWorkflow(config, db_config, dataset_spec=dataset_spec)

    # Handle other workflows through unified registry
    return UnifiedWorkflowRegistry.create_workflow(
        workflow_name, config, db_config, **kwargs
    )


def create_dataset_workflow(
    template_name: Optional[str] = None,
    custom_spec: Optional[DatasetSpec] = None,
    config: Optional[WorkflowConfig] = None,
    db_config=None,
    **workflow_counts,
) -> DatasetWorkflow:
    """
    Create a dataset workflow from template, custom specification, or workflow counts.

    Args:
        template_name: Name of predefined template
        custom_spec: Custom dataset specification
        config: Base workflow configuration
        db_config: Database configuration
        **workflow_counts: Direct workflow counts (people=1000, companies=100)

    Returns:
        DatasetWorkflow instance

    Raises:
        ValueError: If parameters are invalid
    """
    # Count how many ways the user is trying to specify the dataset
    spec_methods = sum(
        [template_name is not None, custom_spec is not None, bool(workflow_counts)]
    )

    if spec_methods == 0:
        raise ValueError("Must provide template_name, custom_spec, or workflow counts")
    if spec_methods > 1:
        raise ValueError(
            "Provide only one of: template_name, custom_spec, or workflow counts"
        )

    # Use default config if none provided
    if config is None:
        config = WorkflowConfig()

    # Create spec based on input method
    if template_name:
        dataset_spec = DatasetSpec.from_template(template_name)
    elif custom_spec:
        dataset_spec = custom_spec
    else:  # workflow_counts provided
        dataset_spec = DatasetSpec.for_full_dataset(**workflow_counts)

    return DatasetWorkflow(config, db_config, dataset_spec)


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


def quick_generate_full_dataset(
    template: str = None, seed: Optional[int] = None, **workflow_counts
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Quick function to generate a complete dataset without database storage.

    Args:
        template: Dataset template to use (optional)
        seed: Random seed for reproducible results
        **workflow_counts: Direct workflow counts (people=1000, companies=100)

    Returns:
        Dictionary with entity types as keys and lists of records as values
    """
    # Determine dataset specification
    if template:
        if template not in DATASET_TEMPLATES:
            raise ValueError(f"Unknown template: {template}")
        dataset_spec = DatasetSpec.from_template(template)
    elif workflow_counts:
        dataset_spec = DatasetSpec.for_full_dataset(**workflow_counts)
    else:
        # Use small demo template as default
        dataset_spec = DatasetSpec.from_template("small_demo")

    result = {}

    # Generate data for each workflow in execution order
    execution_groups = dataset_spec.get_execution_order()

    for group in execution_groups:
        for workflow_name in group:
            count = dataset_spec.workflows[workflow_name]

            # Map workflow name to entity type
            entity_mappings = {"people": "person", "companies": "company"}
            entity_type = entity_mappings.get(workflow_name, workflow_name)

            # Generate data
            config = GeneratorConfig(seed=seed)
            generator = create_generator(entity_type, config)
            result[entity_type] = generator.generate_batch_dicts(count)

    return result
