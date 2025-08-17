"""
Generator factory module for creating generators by entity type.

This module provides a centralized factory for all generators, making it easy
to add new entity types without modifying existing code.
"""

from typing import Optional, Dict, Type, Any, Callable
from earth.generators.base import BaseGenerator, GeneratorConfig
from earth.generators.person import PersonGenerator
from earth.generators.company import CompanyGenerator


def create_generator(
    entity_type: str, config: Optional[GeneratorConfig] = None
) -> BaseGenerator:
    """
    Factory function to create generators by entity type.

    Args:
        entity_type: Type of entity to generate ("person", "company", etc.)
        config: Generator configuration (uses defaults if None)

    Returns:
        Appropriate generator instance

    Raises:
        ValueError: If entity_type is not recognized
    """
    # Import generators here to avoid circular imports

    generators = {
        "person": PersonGenerator,
        "company": CompanyGenerator,
    }

    generator_class = generators.get(entity_type.lower())
    if not generator_class:
        available = list(generators.keys())
        raise ValueError(f"Unknown entity type '{entity_type}'. Available: {available}")

    return generator_class(config)


def get_available_generators() -> Dict[str, Type[BaseGenerator]]:
    """
    Get dictionary of all available generators.

    Returns:
        Dictionary mapping entity names to generator classes
    """

    return {
        "person": PersonGenerator,
        "company": CompanyGenerator,
    }


def get_generator_info(entity_type: str) -> Dict[str, Any]:
    """
    Get information about a specific generator.

    Args:
        entity_type: Type of entity

    Returns:
        Dictionary with generator information

    Raises:
        ValueError: If entity type not found
    """
    try:
        generator_class = get_available_generators()[entity_type.lower()]

        # Create a temporary instance to get metadata
        temp_instance = generator_class()

        return {
            "entity_name": temp_instance.entity_name,
            "required_fields": temp_instance.required_fields,
            "class_name": generator_class.__name__,
            "module": generator_class.__module__,
        }

    except KeyError:
        available = list(get_available_generators().keys())
        raise ValueError(f"Unknown entity type '{entity_type}'. Available: {available}")


def list_available_entities() -> list:
    """
    Get list of all available entity types.

    Returns:
        List of entity type names
    """
    return list(get_available_generators().keys())


# Registry for easy extension
class GeneratorRegistry:
    """
    Registry for managing generator classes.

    This provides a more formal registration system for generators,
    making it easier to extend with new entity types.
    """

    _generators: Dict[str, Type[BaseGenerator]] = {}

    @classmethod
    def register(cls, entity_type: str, generator_class: Type[BaseGenerator]) -> None:
        """
        Register a generator class.

        Args:
            entity_type: Unique entity type name
            generator_class: Generator class to register
        """
        cls._generators[entity_type.lower()] = generator_class

    @classmethod
    def get_generator(cls, entity_type: str) -> Optional[Type[BaseGenerator]]:
        """
        Get a generator class by entity type.

        Args:
            entity_type: Entity type name

        Returns:
            Generator class or None if not found
        """
        return cls._generators.get(entity_type.lower())

    @classmethod
    def list_entities(cls) -> list:
        """Get list of registered entity types."""
        return list(cls._generators.keys())

    @classmethod
    def create_generator(
        cls,
        entity_type: str,
        config: Optional[GeneratorConfig] = None,
    ) -> BaseGenerator:
        """
        Create a generator instance by entity type.

        Args:
            entity_type: Entity type name
            config: Generator configuration

        Returns:
            Generator instance

        Raises:
            ValueError: If entity type not found
        """
        generator_class = cls.get_generator(entity_type)
        if not generator_class:
            available = cls.list_entities()
            raise ValueError(
                f"Unknown entity type '{entity_type}'. Available: {available}"
            )

        return generator_class(config)


# Auto-register available generators
def _auto_register_generators() -> None:
    """Automatically register all available generators."""
    generators = get_available_generators()
    for entity_type, generator_class in generators.items():
        GeneratorRegistry.register(entity_type, generator_class)


# Register generators when module is imported
_auto_register_generators()


# Decorator for easy generator registration
def register_generator(entity_type: str) -> Callable[[type[Any]], type[Any]]:
    """
    Decorator to automatically register generators.

    Usage:
        @register_generator("product")
        class ProductGenerator(BaseGenerator[ProductProfile]):
            ...
    """

    def decorator(generator_class: Type[BaseGenerator]) -> Type[BaseGenerator]:
        GeneratorRegistry.register(entity_type, generator_class)
        return generator_class

    return decorator
