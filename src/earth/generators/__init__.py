"""
Earth Generators Module.

This package provides a unified system for generating realistic synthetic data
for various entity types using a consistent BaseGenerator interface.

The system supports:
- Person profiles with demographics, career, and contact data
- Company profiles with business and financial data
- Factory pattern for easy generator creation
- Extensible registry system for new entity types
"""

from typing import Optional, List, Dict, Any, cast

# Import base infrastructure
from .base import BaseGenerator, GeneratorConfig

# Import specific generators
from .person import (
    PersonGenerator,
    PersonProfile,
    generate_person,
    generate_multiple_persons,
)
from .company import CompanyGenerator, CompanyProfile

# Import factory functions
from .factory import (
    create_generator,
    get_available_generators,
    get_generator_info,
    list_available_entities,
    GeneratorRegistry,
    register_generator,
)

# Import career helper utilities
from .career import (
    generate_career_profile,
    generate_unemployment_profile,
    determine_career_level,
    select_industry,
    calculate_salary,
)

__all__ = [
    # Base infrastructure
    "BaseGenerator",
    "GeneratorConfig",
    # Person generator
    "PersonGenerator",
    "PersonProfile",
    "generate_person",  # Backward compatibility
    "generate_multiple_persons",  # Backward compatibility
    # Company generator
    "CompanyGenerator",
    "CompanyProfile",
    # Factory functions
    "create_generator",
    "get_available_generators",
    "get_generator_info",
    "list_available_entities",
    "GeneratorRegistry",
    "register_generator",
    # Career utilities
    "generate_career_profile",
    "generate_unemployment_profile",
    "determine_career_level",
    "select_industry",
    "calculate_salary",
]

# Quick access to entity information
AVAILABLE_ENTITIES = {
    "person": {
        "generator_class": PersonGenerator,
        "profile_class": PersonProfile,
        "description": "Individual person profiles with demographics and career data",
        "example_fields": [
            "person_id",
            "first_name",
            "last_name",
            "email",
            "age",
            "job_title",
            "annual_income",
            "employment_status",
            "education_level",
        ],
        "use_cases": [
            "User account simulation",
            "Customer database testing",
            "HR system data",
            "Demographics analysis",
        ],
    },
    "company": {
        "generator_class": CompanyGenerator,
        "profile_class": CompanyProfile,
        "description": "Company profiles with business and financial data",
        "example_fields": [
            "company_id",
            "company_name",
            "legal_name",
            "industry",
            "employee_count",
            "annual_revenue",
            "company_size",
            "founded_year",
        ],
        "use_cases": [
            "B2B CRM testing",
            "Market research simulation",
            "Financial analysis",
            "Industry benchmarking",
        ],
    },
}


def get_entity_info_detailed(entity_type: str) -> Dict[str, Any]:
    """
    Get detailed information about an entity type.

    Args:
        entity_type: Type of entity ('person' or 'company')

    Returns:
        Detailed information dictionary including:
        - generator_class: The generator class
        - profile_class: The profile data class
        - description: What this entity represents
        - example_fields: Key fields generated
        - use_cases: Common use cases
        - required_fields: Validation requirements
        - class_name: Generator class name
        - module: Generator module path

    Raises:
        ValueError: If entity type not found

    Example:
        >>> info = get_entity_info_detailed('person')
        >>> print(info['description'])
        Individual person profiles with demographics and career data
    """
    if entity_type not in AVAILABLE_ENTITIES:
        available = list(AVAILABLE_ENTITIES.keys())
        raise ValueError(f"Unknown entity type '{entity_type}'. Available: {available}")

    info = AVAILABLE_ENTITIES[entity_type].copy()

    # Add runtime information from factory
    try:
        factory_info = get_generator_info(entity_type)
        info.update(
            {
                "required_fields": factory_info["required_fields"],
                "class_name": factory_info["class_name"],
                "module": factory_info["module"],
            }
        )
    except Exception as e:
        # Factory info optional, but log if there's an issue
        info["factory_error"] = str(e)

    return info


def print_generators_summary() -> None:
    """
    Print a comprehensive summary of all available generators.

    Displays version info, available entities, usage examples, and
    common patterns for using the generator system.
    """
    print(f"Earth Generators System v{__version__}")
    print("=" * 60)

    print(f"\nAvailable Entity Types ({len(AVAILABLE_ENTITIES)}):")
    print("-" * 40)

    for entity_type, info in AVAILABLE_ENTITIES.items():
        print(f"\n📊 {entity_type.upper()}")
        print(f"   Description: {info['description']}")
        print(f"   Generator: {info['generator_class'].__name__}")
        print(f"   Profile: {info['profile_class'].__name__}")
        print(f"   Key fields: {', '.join(info['example_fields'][:5])}...")
        if "use_cases" in info:
            print(f"   Use cases: {', '.join(info['use_cases'][:2])}...")

    print(f"\n" + "=" * 60)
    print(f"Usage Examples:")
    print("-" * 40)

    print(f"\n🏭 Factory Pattern (Recommended):")
    print(f"   from earth.generators import create_generator, GeneratorConfig")
    print(f"   ")
    print(f"   # Create generator with configuration")
    print(f"   config = GeneratorConfig(seed=42, locale='en_US')")
    print(f"   generator = create_generator('person', config)")
    print(f"   ")
    print(f"   # Generate single profile")
    print(f"   profile = generator.generate_profile()")
    print(f"   ")
    print(f"   # Generate batch as objects")
    print(f"   profiles = generator.generate_batch(100)")
    print(f"   ")
    print(f"   # Generate batch as dictionaries (database-ready)")
    print(f"   data = generator.generate_batch_dicts(100)")

    print(f"\n🔧 Direct Instantiation:")
    print(f"   from earth.generators import PersonGenerator, CompanyGenerator")
    print(f"   ")
    print(f"   # Direct generator creation")
    print(f"   person_gen = PersonGenerator()")
    print(f"   company_gen = CompanyGenerator()")
    print(f"   ")
    print(f"   # Generate profiles")
    print(f"   person = person_gen.generate_profile()")
    print(f"   company = company_gen.generate_profile()")

    print(f"\n⚡ Quick Generation:")
    print(f"   from earth.generators import quick_generate")
    print(f"   ")
    print(f"   # Generate 50 people")
    print(f"   people = quick_generate('person', count=50, seed=123)")
    print(f"   ")
    print(f"   # Generate 10 companies")
    print(f"   companies = quick_generate('company', count=10)")

    print(f"\n🔄 Legacy Compatibility:")
    print(f"   from earth.generators import generate_person")
    print(f"   ")
    print(f"   # Old-style generation (still works)")
    print(f"   profile = generate_person(seed=42)")

    print(f"\n📋 Validation & Stats:")
    print(f"   # Validate generated data")
    print(f"   is_valid = validate_entity_data('person', data)")
    print(f"   ")
    print(f"   # Get generation statistics")
    print(f"   stats = generator.get_generation_stats(profiles)")

    print(f"\n" + "=" * 60)


# Convenience functions for common operations
def quick_generate(
    entity_type: str, count: int = 1, seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Quick generation function for any entity type.

    This is the fastest way to generate entity data when you don't need
    to customize the generator configuration.

    Args:
        entity_type: Type of entity to generate ('person' or 'company')
        count: Number of entities to generate
        seed: Random seed for reproducible results

    Returns:
        List of entity dictionaries ready for database storage

    Raises:
        ValueError: If entity_type is not recognized

    Example:
        >>> # Generate 100 people
        >>> people = quick_generate('person', count=100, seed=42)
        >>> print(f"Generated {len(people)} people")
        Generated 100 people

        >>> # Generate 25 companies
        >>> companies = quick_generate('company', count=25)
        >>> print(companies[0]['company_name'])
        Acme Industries Inc
    """
    config = GeneratorConfig(seed=seed)
    generator = create_generator(entity_type, config)
    return cast(List[Dict[str, Any]], generator.generate_batch_dicts(count))


def validate_entity_data(entity_type: str, data: List[Dict[str, Any]]) -> bool:
    """
    Validate entity data against the appropriate generator's requirements.

    Checks that all required fields are present and have valid values
    according to the generator's validation rules.

    Args:
        entity_type: Type of entity ('person' or 'company')
        data: List of entity dictionaries to validate

    Returns:
        True if all data is valid, False otherwise

    Example:
        >>> data = quick_generate('person', count=5)
        >>> is_valid = validate_entity_data('person', data)
        >>> print(f"Data is valid: {is_valid}")
        Data is valid: True
    """
    try:
        generator = create_generator(entity_type)

        # Validate each record
        for record in data:
            # Check required fields exist and are not None
            for field in generator.required_fields:
                if field not in record or record[field] is None:
                    return False

            # Run custom validation if available
            if hasattr(generator, "_custom_validation"):
                if not generator._custom_validation(record):
                    return False

        return True

    except Exception:
        return False


def get_generator_capabilities() -> Dict[str, Dict[str, Any]]:
    """
    Get comprehensive information about all generator capabilities.

    Returns:
        Dictionary with detailed information about each generator's
        capabilities, fields, validation rules, and statistics.

    Example:
        >>> caps = get_generator_capabilities()
        >>> print(caps['person']['required_fields'])
        ['person_id', 'first_name', 'last_name', 'email', 'age', 'job_title', 'annual_income']
    """
    capabilities = {}

    for entity_type in AVAILABLE_ENTITIES.keys():
        try:
            # Get basic info
            info = get_entity_info_detailed(entity_type)

            # Create temporary generator to inspect capabilities
            generator = create_generator(entity_type)

            capabilities[entity_type] = {
                "description": info["description"],
                "required_fields": generator.required_fields,
                "generator_class": info["generator_class"].__name__,
                "profile_class": info["profile_class"].__name__,
                "example_fields": info["example_fields"],
                "use_cases": info.get("use_cases", []),
                "has_custom_validation": hasattr(generator, "_custom_validation"),
                "has_custom_stats": hasattr(generator, "_get_custom_stats"),
                "config_options": {
                    "locale": "Faker locale (default: en_US)",
                    "seed": "Random seed for reproducibility",
                    "batch_size": "Default batch size for operations",
                },
            }

        except Exception as e:
            capabilities[entity_type] = {
                "error": f"Failed to inspect generator: {str(e)}"
            }

    return capabilities


# Registry inspection functions
def inspect_registry() -> Dict[str, Any]:
    """
    Inspect the current state of the generator registry.

    Returns:
        Dictionary with registry information including registered
        generators and their metadata.
    """
    return {
        "registered_entities": GeneratorRegistry.list_entities(),
        "total_generators": len(GeneratorRegistry.list_entities()),
        "available_via_factory": list_available_entities(),
        "version": __version__,
    }


# Module health check
def health_check() -> Dict[str, Any]:
    """
    Perform a health check on the generators system.

    Tests that all generators can be created and generate valid data.

    Returns:
        Dictionary with health check results.
    """
    results = cast(
        Dict[str, Any],
        {
            "system_version": __version__,
            "total_entities": len(AVAILABLE_ENTITIES),
            "health_status": "healthy",
            "generators": {},
            "errors": [],
        },
    )

    for entity_type in AVAILABLE_ENTITIES.keys():
        try:
            # Test generator creation
            generator = create_generator(entity_type)

            # Test single generation
            profile = generator.generate_profile()

            # Test validation
            is_valid = generator.validate_profile(profile)

            # Test batch generation
            batch = generator.generate_batch(2)
            batch_valid = generator.validate_batch(batch)

            results["generators"][entity_type] = {
                "creation": "ok",
                "single_generation": "ok",
                "single_validation": is_valid,
                "batch_generation": "ok",
                "batch_validation": batch_valid,
                "overall_status": "healthy" if is_valid and batch_valid else "warning",
            }

        except Exception as e:
            results["generators"][entity_type] = {"status": "error", "error": str(e)}
            results["errors"].append(f"{entity_type}: {str(e)}")
            results["health_status"] = "degraded"

    return results
