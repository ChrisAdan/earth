"""
Workflows package for Earth data generation.

This package contains all workflow implementations for generating
different types of synthetic data entities.
"""

from .base import (
    BaseWorkflow,
    WorkflowConfig,
    WorkflowResult,
    WorkflowStatus,
    WorkflowRegistry,
    register_workflow,
)

from .generate_people import PeopleWorkflow
from .generate_companies import CompaniesWorkflow
from .full_dataset import FullDatasetWorkflow, DatasetSpec, WorkflowStep

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
    # Workflow implementations
    "PeopleWorkflow",
    "CompaniesWorkflow",
    "FullDatasetWorkflow",
    # Supporting classes
    "DatasetSpec",
    "WorkflowStep",
]

# Version info
__version__ = "0.1.0"

# Available workflow types (for CLI discovery)
AVAILABLE_WORKFLOWS = {
    "people": {
        "class": PeopleWorkflow,
        "description": "Generate person profiles with demographic and career data",
        "default_count": 1000,
        "schema": "raw",
        "table": "persons",
    },
    "companies": {
        "class": CompaniesWorkflow,
        "description": "Generate company profiles with business and financial data",
        "default_count": 100,
        "schema": "raw",
        "table": "companies",
    },
    "full_dataset": {
        "class": FullDatasetWorkflow,
        "description": "Generate complete dataset with all entity types",
        "default_count": None,  # Uses DatasetSpec defaults
        "schema": "raw",
        "table": "multiple",
    },
}


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
    if workflow_name not in AVAILABLE_WORKFLOWS:
        available = list(AVAILABLE_WORKFLOWS.keys())
        raise ValueError(f"Unknown workflow '{workflow_name}'. Available: {available}")

    return AVAILABLE_WORKFLOWS[workflow_name].copy()


def list_available_workflows() -> list:
    """
    Get list of all available workflow names.

    Returns:
        List of workflow names
    """
    return list(AVAILABLE_WORKFLOWS.keys())


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
        return FullDatasetWorkflow(config, db_config, dataset_spec)
    else:
        # Use registry for other workflows
        return WorkflowRegistry.create_workflow(workflow_name, config, db_config)
