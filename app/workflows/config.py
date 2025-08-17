"""
Configuration module for dataset orchestration. Specifies available workflows
"""

# Available workflows for CLI display
AVAILABLE_WORKFLOWS = {
    "people": {
        "description": "Generate individual person profiles with demographics and career data",
        "default_count": 1000,
    },
    "companies": {
        "description": "Generate company profiles with business and financial data",
        "default_count": 100,
    },
    "full_dataset": {
        "description": "Generate a complete synthetic dataset with people and companies",
        "default_count": None,
    },
}

# Dataset templates for common use cases
DATASET_TEMPLATES = {
    "small_demo": {
        "description": "Small dataset for demos and testing",
        "workflows": {
            "people":50,
            "companies":10
        },
    },
    "medium_dev": {
        "description": "Medium dataset for development work",
        "workflows": {
            "people":50,
            "companies":10
        }
    },
    "large_production": {
        "description": "Large dataset for production-like scenarios",

        "workflows": {
            "people":50,
            "companies":10
        }    
    },
}

# Core workflow configurations - Updated to match actual implementation
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
    },
}