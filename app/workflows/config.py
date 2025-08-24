# File: app/workflows/config.py

"""
Configuration module for dataset orchestration. Specifies available workflows
"""

# Available workflows for CLI display - UPDATED with better full_dataset support
AVAILABLE_WORKFLOWS = {
    "people": {
        "description": "Generate individual person profiles with demographics and career data",
        "default_count": 1000,
        "entity_type": "person",
        "schema": "raw",
        "table": "persons",
    },
    "companies": {
        "description": "Generate company profiles with business and financial data",
        "default_count": 100,
        "entity_type": "company",
        "schema": "raw",
        "table": "companies",
    },
    "full_dataset": {
        "description": "Generate a complete synthetic dataset with people and companies",
        "default_count": None,
        "entity_type": "orchestrated",
        "schema": "raw",
        "table": "multiple",
        "component_workflows": {
            "companies": {"default_count": 100, "dependency_order": 1},
            "people": {
                "default_count": 1000,
                "dependency_order": 2,
                "depends_on": ["companies"],
            },
        },
    },
}

# Dataset templates for common use cases
DATASET_TEMPLATES = {
    "small_demo": {
        "description": "Small dataset for demos and testing",
        "workflows": {"companies": 10, "people": 50},
        "dependencies": {"people": ["companies"]},
    },
    "medium_dev": {
        "description": "Medium dataset for development work",
        "workflows": {"companies": 50, "people": 500},
        "dependencies": {"people": ["companies"]},
    },
    "large_production": {
        "description": "Large dataset for production-like scenarios",
        "workflows": {"companies": 200, "people": 5000},
        "dependencies": {"people": ["companies"]},
    },
}

# Core workflow configurations
WORKFLOW_CONFIGS = {
    "people": {
        "entity_type": "person",
        "description": "Generate person profiles with demographic and career data",
        "default_count": 1000,
        "schema": "raw",
        "table": "persons",
        "dependencies": [],
    },
    "companies": {
        "entity_type": "company",
        "description": "Generate company profiles with business and financial data",
        "default_count": 100,
        "schema": "raw",
        "table": "companies",
        "dependencies": [],
    },
    "full_dataset": {
        "entity_type": "orchestrated",
        "description": "Generate a complete synthetic dataset with multiple entity types",
        "default_count": None,  # Uses DatasetSpec
        "schema": "raw",
        "table": "multiple",
        "dependencies": [],
        "orchestrated": True,
        "component_workflows": ["companies", "people"],  # Extensible list
    },
}


def get_full_dataset_defaults() -> dict:
    """
    Get default configuration for full dataset workflow.
    Makes it easy to extend with new workflow types.

    Returns:
        Dictionary with default counts and dependencies for full dataset
    """
    full_dataset_config = AVAILABLE_WORKFLOWS["full_dataset"]

    defaults = {"workflows": {}, "dependencies": {}}

    # Build from component workflows
    for workflow_name, config in full_dataset_config["component_workflows"].items():
        defaults["workflows"][workflow_name] = config["default_count"]
        if "depends_on" in config:
            defaults["dependencies"][workflow_name] = config["depends_on"]

    return defaults


def validate_full_dataset_ratios(workflows: dict) -> list:
    """
    Validate ratios between different workflow counts.

    Args:
        workflows: Dictionary of workflow_name -> count

    Returns:
        List of validation warnings (empty if all good)
    """
    warnings = []

    if "people" in workflows and "companies" in workflows:
        people_count = workflows["people"]
        companies_count = workflows["companies"]

        if companies_count > 0:
            ratio = people_count / companies_count
            if ratio < 5:
                warnings.append(
                    f"People-to-companies ratio is {ratio:.1f} (recommended: 5-50)"
                )
            elif ratio > 50:
                warnings.append(
                    f"People-to-companies ratio is {ratio:.1f} (recommended: 5-50)"
                )

    return warnings


def get_workflow_dependencies() -> dict:
    """
    Get standard dependencies between workflows.
    Makes dependencies explicit and extensible.

    Returns:
        Dictionary mapping workflow names to their dependencies
    """
    return {
        "people": ["companies"],  # People depend on companies existing
        # Add new workflow dependencies here as system grows
    }
