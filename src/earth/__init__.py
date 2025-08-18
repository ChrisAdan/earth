"""
Earth - Realistic synthetic data generation for testing and development.

A comprehensive toolkit for generating realistic synthetic data including:
- Person profiles with demographics and career progression
- Company data with industry-specific characteristics
- Marketing campaigns and product information
- Vehicle ownership and automotive data

Modern Architecture Features:
- Factory pattern for generator creation
- Pluggable generator registry system
- Unified BaseGenerator interface
- Database integration via DuckDB
- Modular installation for specific use cases

Usage Examples:
    # Quick generation (recommended)
    from earth import quick_generate
    people = quick_generate('person', count=100, seed=42)

    # Factory pattern
    from earth import create_generator, GeneratorConfig
    config = GeneratorConfig(seed=42, locale='en_US')
    generator = create_generator('person', config)
    profiles = generator.generate_batch(50)

    # Legacy compatibility
    from earth import generate_person
    person = generate_person(seed=42)
"""

from typing import Optional, List, Dict, Any, TypedDict

__version__ = "0.3.0"
__author__ = "Chris Adan"
__description__ = "Realistic synthetic data generation for testing and development"

# Core imports - always available
from .core import (
    # Database functionality
    DatabaseConfig,
    connect_to_duckdb,
    operate_on_table,
    get_table_info,
    setup_logging,
    log,
    create_dev_database,
    create_prod_database,
    create_test_database,
    get_module_info as get_core_module_info,
    # Data models and utilities
    PersonProfile,
    CareerProfile,
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

# Generator system imports - always available
from .generators import (
    # Base infrastructure
    BaseGenerator,
    GeneratorConfig,
    # Specific generators
    PersonGenerator,
    CompanyGenerator,
    CompanyProfile,
    # Factory functions
    create_generator,
    get_available_generators,
    get_generator_info,
    list_available_entities,
    GeneratorRegistry,
    register_generator,
    # Career utilities
    generate_career_profile,
    generate_unemployment_profile,
    determine_career_level,
    select_industry,
    calculate_salary,
    # Legacy compatibility functions
    generate_person,
    generate_multiple_persons,
    # Convenience functions
    quick_generate,
    validate_entity_data,
    get_generator_capabilities,
    get_entity_info_detailed,
    print_generators_summary,
    inspect_registry,
    health_check,
)


def _optional_import(module_path: str, install_extra: str) -> Any:
    """Helper to conditionally import optional modules."""
    try:
        import importlib

        return importlib.import_module(module_path, "earth")
    except ImportError:

        def _missing_module(*args: Any, **kwargs: Any) -> None:
            raise ImportError(
                f"This functionality requires the '{install_extra}' extra. "
                f"Install with: pip install earth[{install_extra}]"
            )

        return type(
            "MissingModule", (), {"__getattr__": lambda self, name: _missing_module}
        )()


# Optional module imports
campaigns = _optional_import(".modules.campaigns", "campaigns")
automotive = _optional_import(".modules.automotive", "automotive")

# Main API exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
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


# Module availability checker
def check_module_availability() -> Dict[str, bool]:
    """
    Check which optional modules are available.

    Returns:
        Dict mapping module names to availability status
    """
    availability = {}

    optional_modules = {
        "campaigns": "earth.modules.campaigns",
        "automotive": "earth.modules.automotive",
    }

    for module_name, module_path in optional_modules.items():
        try:
            import importlib

            importlib.import_module(module_path)
            availability[module_name] = True
        except ImportError:
            availability[module_name] = False

    return availability


def get_install_command(module_name: str) -> str:
    """
    Get pip install command for a specific module.

    Args:
        module_name: Name of the optional module

    Returns:
        Pip install command string
    """
    valid_modules = ["campaigns", "automotive", "all"]

    if module_name not in valid_modules:
        raise ValueError(
            f"Unknown module '{module_name}'. Valid modules: {valid_modules}"
        )

    return f"pip install earth[{module_name}]"


class ModulesDict(TypedDict):
    core: List[str]
    generators: List[str]
    optional: List[str]


class PackageInfo(TypedDict):
    name: str
    version: str
    description: str
    author: str
    modules: ModulesDict
    install_extras: Dict[str, str]


# Updated package metadata
PACKAGE_INFO: PackageInfo = {
    "name": "earth",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "modules": {
        "core": ["database", "utils", "models"],
        "generators": ["person", "company", "career", "factory"],
        "optional": ["campaigns", "automotive"],
    },
    "install_extras": {
        "campaigns": "Marketing campaign and product simulation",
        "automotive": "Vehicle ownership and automotive data",
        "all": "All optional modules",
        "dev": "Development dependencies",
    },
}


def info() -> None:
    """Print comprehensive package information and module availability."""
    print(f"🌍 Earth v{__version__}")
    print(f"   {__description__}")
    print()

    # Core modules
    print("📦 Core Modules (always available):")
    for module in PACKAGE_INFO["modules"]["core"]:
        print(f"   ✅ {module}")
    print()

    # Generator system
    print("🏭 Generator System:")
    for module in PACKAGE_INFO["modules"]["generators"]:
        print(f"   ✅ {module}")

    # Show available entity types
    available_entities = list_available_entities()
    print(f"   📊 Available Entities: {', '.join(available_entities)}")
    print()

    # Optional modules
    availability = check_module_availability()
    print("🔧 Optional Modules:")
    for module in PACKAGE_INFO["modules"]["optional"]:
        status = "✅ Available" if availability[module] else "❌ Not installed"
        print(f"   {status} {module}")
        if not availability[module]:
            print(f"      Install: {get_install_command(module)}")
    print()

    if not all(availability.values()):
        print("💡 Install all modules: pip install earth[all]")

    print("\n🚀 Quick Start:")
    print("   # Generate 100 people")
    print("   from earth import quick_generate")
    print("   people = quick_generate('person', count=100, seed=42)")
    print()
    print("   # Use factory pattern")
    print("   from earth import create_generator, GeneratorConfig")
    print("   config = GeneratorConfig(seed=42)")
    print("   generator = create_generator('person', config)")
    print("   profiles = generator.generate_batch(50)")
    print()
    print("   # Legacy compatibility")
    print("   from earth import generate_person")
    print("   person = generate_person(seed=42)")


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.

    Returns:
        Dictionary containing package info, module availability,
        generator capabilities, and system health status.
    """
    return {
        "package": PACKAGE_INFO,
        "module_availability": check_module_availability(),
        "generator_capabilities": get_generator_capabilities(),
        "registry_info": inspect_registry(),
        "health_check": health_check(),
        "core_module_info": get_core_module_info(),
    }


def run_diagnostics() -> None:
    """Run comprehensive system diagnostics and print results."""
    print("🔍 Earth System Diagnostics")
    print("=" * 50)

    # Package info
    info()

    # Generator system summary
    print("\n📊 Generator System Summary:")
    print_generators_summary()

    # Health check
    print("\n🏥 System Health Check:")
    health = health_check()
    print(f"Overall Status: {health['health_status'].upper()}")

    for entity_type, status in health["generators"].items():
        if isinstance(status, dict) and "overall_status" in status:
            emoji = "✅" if status["overall_status"] == "healthy" else "⚠️"
            print(f"{emoji} {entity_type}: {status['overall_status']}")

    if health["errors"]:
        print("\n❌ Errors found:")
        for error in health["errors"]:
            print(f"   - {error}")


# Convenience aliases for common patterns
def generate_people(
    count: int = 1, seed: Optional[int] = None, **kwargs: Any
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate people.

    Args:
        count: Number of people to generate
        seed: Random seed for reproducibility
        **kwargs: Additional configuration options

    Returns:
        List of person dictionaries
    """
    return quick_generate("person", count=count, seed=seed)


def generate_companies(
    count: int = 1, seed: Optional[int] = None, **kwargs: Any
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate companies.

    Args:
        count: Number of companies to generate
        seed: Random seed for reproducibility
        **kwargs: Additional configuration options

    Returns:
        List of company dictionaries
    """
    return quick_generate("company", count=count, seed=seed)


# Add convenience functions to exports
__all__.extend(
    [
        "get_system_info",
        "run_diagnostics",
        "generate_people",
        "generate_companies",
    ]
)

if __name__ == "__main__":
    run_diagnostics()
