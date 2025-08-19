"""
Earth Core Module

This module provides the foundational components for the Earth data generation system,
including database operations, data models, and utility functions.

Main Components:
- DatabaseConfig: Database configuration management
- PersonProfile: Person data model
- CareerProfile: Career information model
- Database operations: CRUD operations via DuckDB
- Logging utilities
- Career and industry data structures

Usage:
    from earth.core import DatabaseConfig, PersonProfile, connect_to_duckdb

    # Create database config
    config = DatabaseConfig.for_dev()

    # Connect to database
    conn = connect_to_duckdb(config)

    # Use person profile model
    person = PersonProfile(...)
"""

from .. import __version__

# Core database functionality
from .loader import (
    DatabaseConfig,
    connect_to_duckdb,
    operate_on_table,
    get_table_info,
    setup_logging,
    log,
)

# Data models and utilities
from .utils import (
    # Data classes
    PersonProfile,
    CareerProfile,
    # Enums
    CareerLevel,
    IndustryMetadata,
    # Constants
    MIN_AGE,
    MAX_AGE,
    US_JOB_TITLES,
    EMAIL_DOMAINS,
    CAREER_TITLES,
    SALARY_RANGES,
    EMPLOYMENT_STATUSES,
    EDUCATION_LEVELS,
    MARITAL_STATUSES,
    COMPANY_SIZE_CATEGORIES,
    BUSINESS_TYPES,
    LEGAL_SUFFIXES,
    REVENUE_RANGES,
    CREDIT_RATINGS,
    GROWTH_STAGES,
)

__author__ = "Chris Adan"

# Public API - what gets imported with "from earth.core import *"
__all__ = [
    # Database operations
    "DatabaseConfig",
    "connect_to_duckdb",
    "operate_on_table",
    "get_table_info",
    "setup_logging",
    "log",
    # Data models
    "PersonProfile",
    "CareerProfile",
    # Enums
    "CareerLevel",
    "IndustryMetadata",
    # Constants
    "MIN_AGE",
    "MAX_AGE",
    "US_JOB_TITLES",
    "EMAIL_DOMAINS",
    "CAREER_TITLES",
    "SALARY_RANGES",
    "EMPLOYMENT_STATUSES",
    "EDUCATION_LEVELS",
    "MARITAL_STATUSES",
    "COMPANY_SIZE_CATEGORIES",
    "BUSINESS_TYPES",
    "LEGAL_SUFFIXES",
    "REVENUE_RANGES",
    "CREDIT_RATINGS",
    "GROWTH_STAGES",
]


# Module-level convenience functions
def create_dev_database(schema_name: str = "raw") -> "DatabaseConfig":
    """
    Convenience function to create a development database configuration.

    Args:
        schema_name: Schema name for the database

    Returns:
        DatabaseConfig configured for development environment
    """
    return DatabaseConfig.for_dev(schema_name)


def create_prod_database(schema_name: str = "raw") -> "DatabaseConfig":
    """
    Convenience function to create a production database configuration.

    Args:
        schema_name: Schema name for the database

    Returns:
        DatabaseConfig configured for production environment
    """
    return DatabaseConfig.for_prod(schema_name)


def create_test_database(schema_name: str = "test") -> "DatabaseConfig":
    """
    Convenience function to create a test database configuration.

    Args:
        schema_name: Schema name for the database

    Returns:
        DatabaseConfig configured for testing environment
    """
    return DatabaseConfig.for_testing(schema_name)


# Add convenience functions to __all__
__all__.extend(
    [
        "create_dev_database",
        "create_prod_database",
        "create_test_database",
    ]
)

# Module metadata
_MODULE_INFO = {
    "name": "earth.core",
    "description": "Core data generation and database management functionality",
    "version": __version__,
    "components": {
        "database": "DuckDB interface and configuration management",
        "models": "Data models for person and career profiles",
        "utils": "Industry data, career levels, and utility constants",
        "logging": "Centralized logging configuration",
    },
}


def get_module_info() -> dict:
    """
    Get information about the core module.

    Returns:
        Dictionary containing module metadata
    """
    return _MODULE_INFO.copy()


# Add to public API
__all__.append("get_module_info")
