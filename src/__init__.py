"""
Earth: Synthetic data generation platform for analytics engineering.

This is the top-level package entry point that re-exports all functionality
from the earth module. Version information is centralized in earth.__init__.py.
"""

__author__ = "Chris Adan"

# Import everything from the main earth module
from earth import (
    # Version info (centralized)
    __version__,
    __description__,
    # Core database functionality
    DatabaseConfig,
    connect_to_duckdb,
    operate_on_table,
    get_table_info,
    setup_logging,
    log,
    create_dev_database,
    create_prod_database,
    create_test_database,
    get_core_module_info,
    # Data models
    PersonProfile,
    CareerProfile,
    CompanyProfile,
    CareerLevel,
    IndustryMetadata,
    # Generator infrastructure
    BaseGenerator,
    GeneratorConfig,
    PersonGenerator,
    CompanyGenerator,
    # Factory pattern (recommended)
    create_generator,
    get_available_generators,
    get_generator_info,
    list_available_entities,
    GeneratorRegistry,
    register_generator,
    # Quick generation functions
    quick_generate,
    validate_entity_data,
    get_generator_capabilities,
    get_entity_info_detailed,
    # Career utilities
    generate_career_profile,
    generate_unemployment_profile,
    determine_career_level,
    select_industry,
    calculate_salary,
    # Legacy compatibility (backward compatibility)
    generate_person,
    generate_multiple_persons,
    # System utilities
    print_generators_summary,
    inspect_registry,
    health_check,
    check_module_availability,
    get_install_command,
    info,
    get_system_info,
    run_diagnostics,
    generate_people,
    generate_companies,
    # Optional modules
    campaigns,
    automotive,
    # Constants (from core)
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

# Re-export everything - this makes src/__init__.py a clean pass-through
__all__ = [
    # Version info
    "__version__",
    "__description__",
    # Core database functionality
    "DatabaseConfig",
    "connect_to_duckdb",
    "operate_on_table",
    "get_table_info",
    "setup_logging",
    "log",
    "create_dev_database",
    "create_prod_database",
    "create_test_database",
    "get_core_module_info",
    # Data models
    "PersonProfile",
    "CareerProfile",
    "CompanyProfile",
    "CareerLevel",
    "IndustryMetadata",
    # Generator infrastructure
    "BaseGenerator",
    "GeneratorConfig",
    "PersonGenerator",
    "CompanyGenerator",
    # Factory pattern (recommended)
    "create_generator",
    "get_available_generators",
    "get_generator_info",
    "list_available_entities",
    "GeneratorRegistry",
    "register_generator",
    # Quick generation functions
    "quick_generate",
    "validate_entity_data",
    "get_generator_capabilities",
    "get_entity_info_detailed",
    # Career utilities
    "generate_career_profile",
    "generate_unemployment_profile",
    "determine_career_level",
    "select_industry",
    "calculate_salary",
    # Legacy compatibility (backward compatibility)
    "generate_person",
    "generate_multiple_persons",
    # System utilities
    "print_generators_summary",
    "inspect_registry",
    "health_check",
    "check_module_availability",
    "get_install_command",
    "info",
    "get_system_info",
    "run_diagnostics",
    "generate_people",
    "generate_companies",
    # Optional modules
    "campaigns",
    "automotive",
    # Constants (from core)
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
